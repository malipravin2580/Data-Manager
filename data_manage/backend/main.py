"""FastAPI Backend for Data Manager."""

from datetime import datetime
from pathlib import Path
import sys
from typing import Any, Dict, List, Literal, Optional
import io

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data_manager import DataManager


app = FastAPI(
    title="Data Manager API",
    description="REST API for managing CSV, JSON, Excel, Parquet files",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
dm = DataManager(str(DATA_DIR))


class FileInfo(BaseModel):
    name: str
    type: str
    size_mb: float
    rows: Optional[int]
    modified: str


class ColumnInfo(BaseModel):
    name: str
    dtype: str
    null_count: int
    unique_count: int


class DataPreview(BaseModel):
    columns: List[ColumnInfo]
    data: List[Dict[str, Any]]
    total_rows: int
    metadata: Dict[str, Any]


class StatsResponse(BaseModel):
    stats: Dict[str, Dict[str, Any]]


class MessageResponse(BaseModel):
    message: str


@app.get("/", response_model=Dict[str, str])
def root() -> Dict[str, str]:
    return {"status": "running", "service": "Data Manager API"}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "healthy", "data_dir": str(DATA_DIR.resolve())}


@app.get("/files", response_model=List[FileInfo])
def list_files(file_type: Optional[str] = None) -> List[FileInfo]:
    files = dm.list_files("*")
    result: List[FileInfo] = []

    for f in files:
        if not f.is_file():
            continue
        if file_type and f.suffix.lower() != f".{file_type.lower()}":
            continue

        info = dm.get_info(f.name)
        modified = info.get("modified")
        result.append(
            FileInfo(
                name=f.name,
                type=info.get("extension", ""),
                size_mb=round(info.get("size_mb", 0.0), 4),
                rows=info.get("row_count"),
                modified=modified.isoformat() if modified else "",
            )
        )

    result.sort(key=lambda x: x.modified, reverse=True)
    return result


@app.post("/upload", response_model=MessageResponse)
async def upload_file(file: UploadFile = File(...)) -> MessageResponse:
    allowed_extensions = {".csv", ".json", ".xlsx", ".xls", ".parquet", ".feather"}
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {sorted(allowed_extensions)}",
        )

    save_path = DATA_DIR / filename
    if save_path.exists():
        raise HTTPException(status_code=409, detail="File already exists")

    contents = await file.read()
    save_path.write_bytes(contents)

    return MessageResponse(message=f"Uploaded {filename}")


@app.post("/upload/replace", response_model=MessageResponse)
async def upload_replace(file: UploadFile = File(...)) -> MessageResponse:
    filename = file.filename or ""
    save_path = DATA_DIR / filename

    contents = await file.read()
    save_path.write_bytes(contents)

    return MessageResponse(message=f"Replaced {filename}")


@app.get("/preview/{filename}", response_model=DataPreview)
def preview_file(
    filename: str,
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
) -> DataPreview:
    try:
        df = dm.load(filename)
        paginated_df = df.iloc[offset : offset + limit]

        columns = [
            ColumnInfo(
                name=str(col),
                dtype=str(dtype),
                null_count=int(df[col].isnull().sum()),
                unique_count=int(df[col].nunique()),
            )
            for col, dtype in df.dtypes.items()
        ]

        return DataPreview(
            columns=columns,
            data=paginated_df.to_dict(orient="records"),
            total_rows=len(df),
            metadata={
                k: (str(v) if isinstance(v, datetime) else v)
                for k, v in df.attrs.items()
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/stats/{filename}", response_model=StatsResponse)
def get_stats(filename: str) -> StatsResponse:
    try:
        df = dm.load(filename)
        stats = df.describe(include="all").to_dict()

        cleaned_stats: Dict[str, Dict[str, Any]] = {}
        for col, col_stats in stats.items():
            cleaned_stats[col] = {
                k: float(v) if hasattr(v, "__float__") else v for k, v in col_stats.items()
            }

        return StatsResponse(stats=cleaned_stats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    path = DATA_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)


@app.get("/export/{filename}")
def export_file(filename: str, format: Literal["csv", "json", "parquet", "xlsx"] = "csv"):
    try:
        df = dm.load(filename)

        output = io.BytesIO()
        output_name = f"{Path(filename).stem}.{format}"

        if format == "csv":
            output.write(df.to_csv(index=False).encode("utf-8"))
            media_type = "text/csv"
        elif format == "json":
            output.write(df.to_json(orient="records", indent=2).encode("utf-8"))
            media_type = "application/json"
        elif format == "parquet":
            df.to_parquet(output, index=False)
            media_type = "application/octet-stream"
        else:
            df.to_excel(output, index=False)
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        output.seek(0)
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={output_name}"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.delete("/file/{filename}", response_model=MessageResponse)
def delete_file(filename: str) -> MessageResponse:
    path = DATA_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    path.unlink()

    meta_path = path.with_suffix(path.suffix + ".meta.json")
    if meta_path.exists():
        meta_path.unlink()

    return MessageResponse(message=f"Deleted {filename}")


@app.get("/search")
def search_files(query: str) -> Dict[str, List[str]]:
    files = dm.list_files("*")
    results = [f.name for f in files if f.is_file() and query.lower() in f.name.lower()]
    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

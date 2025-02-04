from fastapi import FastAPI, File, UploadFile, Form, HTTPException

async def parse_form_data(
    doc_type: str = Form(...),
    file_name: str = Form(None),
    file: UploadFile = File(...)
):
    return {"file_name": file_name, "doc_type": doc_type, "file": file}

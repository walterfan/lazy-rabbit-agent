from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from prompt.domain import PromptCreate, PromptResponse, PromptUpdate, TagBase
from prompt.models import Prompt, Tag
from database import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from util.agent_logger import logger
from util.common_util import get_default_customer_id, get_default_realm_id
import uuid
import csv
import json
import yaml
import io
from pathlib import Path


# Initialize the router
router = APIRouter()

# Helper functions
def get_or_create_tags(db: Session, tags: List[TagBase], created_by: str):
    db_tags = []
    for tag in tags:
        # Check if tag exists
        db_tag = db.query(Tag).filter(Tag.name == tag.name).first()
        if not db_tag:
            # Create new tag
            db_tag = Tag(
                category=tag.category,
                name=tag.name,
                id=str(uuid.uuid4()),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=created_by,
                updated_by=created_by,
                realm_id=get_default_realm_id()
            )
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        db_tags.append(db_tag)
    return db_tags

""" create prompt
curl -X POST "http://localhost:8000/api/v1/prompts/" \
-H "Content-Type: application/json" \
-d '{
    "name": "SQL Generator",
    "description": "Generates SQL from natural language",
    "systemPrompt": "You are a SQL expert...",
    "userPrompt": "Convert this to SQL: {input}",
    "tags": [
        {"category": "prompt", "name": "sql"},
        {"category": "prompt", "name": "generator"}
    ],
    "variables": "input",
    "createdBy": "admin",
    "updatedBy": "admin"
}'
"""
# CRUD Operations
@router.post("/prompts", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
def create_prompt(promptRequest: PromptCreate, db: Session = Depends(get_db)):
    logger.info(f"create_prompt: {promptRequest}")
    # Handle tags
    db_tags = []
    if promptRequest.tags:
        db_tags = get_or_create_tags(db, promptRequest.tags, promptRequest.created_by)

    variables = ""
    if promptRequest.variables:
        variables = ', '.join(promptRequest.variables)

    # Create prompt
    db_prompt = Prompt(
        id=str(uuid.uuid4()),
        name=promptRequest.name,
        description=promptRequest.description,
        system_prompt=promptRequest.system_prompt,
        user_prompt=promptRequest.user_prompt,
        realm_id=get_default_realm_id(),
        variables=variables,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=promptRequest.created_by,
        updated_by=promptRequest.updated_by,
        tags=db_tags
    )

    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    # return PromptResponse based on Prompt

    return PromptResponse(
            id=db_prompt.id,
            name=db_prompt.name,
            description=db_prompt.description,
            systemPrompt=db_prompt.system_prompt,
            userPrompt=db_prompt.user_prompt,
            variables=db_prompt.variables.split(', ') if db_prompt.variables else [],
            tags=[
                TagBase(
                    id=tag.id,
                    category=tag.category,
                    name=tag.name
                ) for tag in db_prompt.tags
            ],
            realmId=db_prompt.realm_id,
            createdAt=db_prompt.created_at,
            updatedAt=db_prompt.updated_at,
            createdBy=db_prompt.created_by,
            updatedBy=db_prompt.updated_by
        )

@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
def read_prompt(prompt_id: str, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
"""
curl "http://localhost:8000/prompt/api/v1/prompts/?tagNames=sql,generator"
"""
@router.get("/prompts", response_model=dict)
def read_prompts(
    skip: int = 0,
    limit: int = 100,
    keyword: Optional[str] = None,
    tag_names: Optional[str] = Query(None, alias="tagNames"),
    db: Session = Depends(get_db)
):
    logger.info(f"read_prompts with keyword: {keyword}, tag_names: {tag_names}")
    query = db.query(Prompt)

    # Apply keyword search if provided
    if keyword:
        keyword = keyword.lower()
        query = query.join(Prompt.tags).filter(
            func.lower(Prompt.name).contains(keyword) |
            func.lower(Prompt.description).contains(keyword) |
            func.lower(Tag.name).contains(keyword)
        ).distinct()
    
    # Apply tag filter if provided (works with or without keyword)
    if tag_names:
        tag_list = [name.strip().lower() for name in tag_names.split(",")]
        query = query.join(Prompt.tags).filter(
            func.lower(Tag.name).in_(tag_list)
        ).distinct()

    total = query.count()
    prompts = query.offset(skip).limit(limit).all()
    
    items = [
        PromptResponse(
            id=prompt.id,
            name=prompt.name,
            description=prompt.description,
            systemPrompt=prompt.system_prompt,
            userPrompt=prompt.user_prompt,
            variables=prompt.variables.split(', ') if prompt.variables else [],
            tags=[
                TagBase(
                    id=tag.id,
                    category=tag.category,
                    name=tag.name
                ) for tag in prompt.tags
            ],
            realmId=prompt.realm_id,
            createdAt=prompt.created_at,
            updatedAt=prompt.updated_at,
            createdBy=prompt.created_by,
            updatedBy=prompt.updated_by
        )
        for prompt in prompts
    ]
    
    return {
        "total": total,
        "items": items
    }

"""
curl -X PUT "http://localhost:8000/prompts/1" \
-H "Content-Type: application/json" \
-d '{
    "tags": [
        {"category": "technology", "name": "sql"},
        {"category": "ai", "name": "nlp"}
    ],
    "updatedBy": "admin"
}'
"""

@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: str, prompt: PromptUpdate, db: Session = Depends(get_db)):
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Update basic fields
    update_data = prompt.dict(exclude_unset=True, exclude={"tags"})
    for field, value in update_data.items():
        setattr(db_prompt, field, value)
    
    # Update tags if provided
    if prompt.tags is not None:
        db_tags = get_or_create_tags(db, prompt.tags, prompt.updated_by)
        db_prompt.tags = db_tags
    
    db_prompt.updated_at = datetime.now()
    db.commit()
    db.refresh(db_prompt)
    #return db_prompt

    return PromptResponse(
        id=db_prompt.id,
        name=db_prompt.name,
        description=db_prompt.description,
        systemPrompt=db_prompt.system_prompt,
        userPrompt=db_prompt.user_prompt,
        variables=db_prompt.variables.split(', ') if prompt.variables else [],
        tags=[
            TagBase(
                id=tag.id,
                category=tag.category,
                name=tag.name
            ) for tag in prompt.tags
        ],
        realmId=db_prompt.realm_id,
        createdAt=db_prompt.created_at,
        updatedAt=db_prompt.updated_at,
        createdBy=db_prompt.created_by,
        updatedBy=db_prompt.updated_by
    )

@router.delete("/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(prompt_id: str, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found " + prompt_id)

    db.delete(prompt)
    db.commit()
    return

# Tag Operations
@router.post("/tags", response_model=TagBase, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagBase, created_by: str = "system", db: Session = Depends(get_db)):
    # Check if tag already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    db_tag = Tag(
        category=tag.category,
        name=tag.name,
        id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=created_by,
        updated_by=created_by
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/tags", response_model=List[TagBase])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Tag)

    if category:
        query = query.filter(Tag.category == category)
    
    if name:
        query = query.filter(Tag.name.contains(name))
    
    return query.offset(skip).limit(limit).all()


@router.post("/prompts/import", response_model=List[PromptResponse], status_code=status.HTTP_201_CREATED)
async def upload_prompts(
    file: UploadFile = File(...),
    created_by: str = "system",
    updated_by: str = "system",
    db: Session = Depends(get_db)
):
    """
    Upload prompts from CSV, JSON, or YAML file.
    Expected formats:
    - CSV: first row as header (name,description,system_prompt,user_prompt,variables,tags)
    - JSON/YAML: array of PromptCreate objects
    """
    file_ext = Path(file.filename).suffix.lower()
    content = await file.read()

    try:
        if file_ext == '.csv':
            # Parse CSV
            csv_data = io.StringIO(content.decode('utf-8'))
            reader = csv.DictReader(csv_data)
            prompts = []
            for row in reader:
                # Convert CSV row to PromptCreate
                tags = []
                if row.get('tags'):
                    tags = [
                        TagBase(category='prompt', name=t.strip())
                        for t in row['tags'].split(',')
                    ]

                prompt = PromptResponse(
                    name=row['name'],
                    description=row.get('description', ''),
                    system_prompt=row.get('system_prompt', ''),
                    user_prompt=row.get('user_prompt', ''),
                    variables=row.get('variables', '').split(',') if row.get('variables') else [],
                    tags=tags,
                    created_by=created_by,
                    updated_by=updated_by
                )
                prompts.append(prompt)

        elif file_ext in ('.json', '.yaml'):
            # Parse JSON/YAML
            if file_ext == '.json':
                data = json.loads(content)
            else:  # yaml
                data = yaml.safe_load(content)

            prompts = []
            for command_name, prompt_data in data.items():
                # Handle tags - can be string or list
                tags = []
                if 'tags' in prompt_data:
                    if isinstance(prompt_data['tags'], str):
                        tags = [TagBase(category='prompt', name=prompt_data['tags'])]
                    elif isinstance(prompt_data['tags'], list):
                        tags = [TagBase(category='prompt', name=tag) for tag in prompt_data['tags']]

                # Handle variables - convert dict to list of variable names
                variables = []
                if 'variables' in prompt_data and isinstance(prompt_data['variables'], dict):
                    variables = list(prompt_data['variables'].keys())

                prompt = PromptResponse(
                    id=str(uuid.uuid4()),
                    name=command_name,
                    description=prompt_data.get('desc', ''),
                    system_prompt=prompt_data.get('system_prompt', ''),
                    user_prompt=prompt_data.get('user_prompt', ''),
                    variables=variables,
                    tags=tags,
                    realmId=prompt_data.get('realm_id', get_default_realm_id()),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    created_by=created_by,
                    updated_by=updated_by
                )
                logger.info(f"Importing prompt: {prompt}")
                prompts.append(prompt)

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload CSV, JSON or YAML"
            )

        # Batch create prompts
        results = []
        for prompt_data in prompts:
            # Reuse your existing create_prompt logic
            response = create_prompt(prompt_data, db)
            results.append(response)

        return results

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )
from fastapi import APIRouter, HTTPException, status
from app.models.todo_models import ResponseTodo, CreateTodo, UpdateTodo
from app.schemas import Todo
from app.dependencies.database import db_dependency
from app.dependencies.auth import auth_dependency
from typing import List


router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/list", response_model=List[ResponseTodo])
async def fetch_all_todos(user: auth_dependency, db: db_dependency) -> List[ResponseTodo]:
    """
    ## Fetch all the todos of current user
    
    ### Args
    - **None**
    
    ### Raises:
    - **400**: Failed to retrieve todos
    - **401**: User is not authenticated
    
    ### Returns:
    - **List[ResponseTodo]**: A list of todos for the current user
    """
    query = db.query(Todo)
    try:
        response = query.filter(Todo.user_id == user["id"]).all()
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/completed", response_model=List[ResponseTodo], summary="Fetch all completed todos")
async def fetch_all_todos(user: auth_dependency, db: db_dependency) -> List[ResponseTodo]:
    """
    ## Fetch all completed todos

    ### Args
    - **None**

    ### Raises:
    - **400**: Failed to retrieve todos
    - **401**: User is not authenticated
    
    ### Returns:
    - **List[ResponseTodo]**: List of completed todos for the current user
    """
    query = db.query(Todo)
    try:
        response = query.filter(Todo.completed == True, Todo.user_id == user["id"]).all()
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/pending", response_model=List[ResponseTodo], summary="Fetch all pending todos")
async def fetch_all_todos(user: auth_dependency, db: db_dependency) -> List[ResponseTodo]:
    """
    ## Fetch all pending todos

    ### Args
    - **None**

    ### Raises:
    - **400**: Failed to retrieve todos
    - **401**: User is not authenticated
    
    ### Returns:
    - **List[ResponseTodo]**: List of pending todos for the current user
    """
    query = db.query(Todo)
    try:
        response = query.filter(Todo.completed == False, Todo.user_id == user["id"]).all()
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/{todo_id}", response_model=ResponseTodo)
async def get_todo(todo_id: str, user: auth_dependency, db: db_dependency) -> ResponseTodo:
    """
    ## Get a single todo by its *id*

    ### Args:
    - **todo_id**: The id of the todo item to retrieve

    ### Raises:
    - **404**: If the todo with the given id is not found
    - **400**: If there is an issue with the database query
    
    ### Returns:
    - **dict[str, str]**: Details of the todo item 
    """
    query = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user["id"])
    if not query.first():
        raise HTTPException(status_code=404, detail="Todo not found")
    try:
        response = query.first()
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.patch("/{todo_id}", response_model=ResponseTodo)
async def update_todo(todo_id: str, todo: UpdateTodo, user: auth_dependency, db: db_dependency) -> ResponseTodo:
    """
    ## Update a todo by its id.

    ### Args:
    - **todo_id**: The id of the todo to update
    - **task** [optional]: The updated task of the todo
    - **completed** [optional]: The updated completed status of the todo

    ### Raises:
    - **404**: If the todo with the given id is not found
    - **400**: If there is an issue with the database query
        
    ### Returns:
    - **dict[str, str]**: The updated todo
    """
    query = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user["id"])
    if not query.first():
        raise HTTPException(status_code=404, detail="Todo not found")
    try:
        updated_todo = query.first()
        if todo.task:
            updated_todo.task = todo.task
        if todo.completed:
            updated_todo.completed = todo.completed
        db.commit()
        db.refresh(updated_todo)
        return updated_todo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("", response_model=ResponseTodo, status_code=status.HTTP_201_CREATED, )
async def create_todo(todo: CreateTodo, user: auth_dependency, db: db_dependency) -> ResponseTodo:
    """
    ## Create a new todo

    ### Args:
    - **todo**: The todo to create

    ### Raises:
    - **400**: If there is an issue with the database query
    - **401**: If the user is not authenticated  
    
    ### Returns:
    - **dict[str, str]**: The created todo
    """
    try:
        new_todo = Todo(**todo.model_dump(), user_id=user["id"])
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/toggle_complete/{todo_id}", response_model=ResponseTodo, summary="Toggles the completed field")
async def mark_as_completed(todo_id: str, user: auth_dependency, db: db_dependency) -> ResponseTodo:
    """
    ## Toggles the completed field of a todo.
            Note: You can acheive this with a patch request as well.
            
    ### Args:
    - **todo_id**: The id of the todo to toggle

    ### Raises:
    - **404**: If the todo with the given id is not found
    - **400**: If there is an issue with the database query

    ### Returns:
    - **dict[str, str]**: The toggled todo
    
    """
    query = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user["id"])
    if not query.first():
        raise HTTPException(status_code=404, detail="Todo not found")
    try:
        updated_todo = query.first()
        if updated_todo.completed:
            updated_todo.completed = False
        else:
            updated_todo.completed = True            
        db.commit()
        db.refresh(updated_todo)
        return updated_todo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete("/{todo_id}", response_model=ResponseTodo)
async def delete_todo(todo_id: str, user: auth_dependency, db: db_dependency) -> ResponseTodo:
    """
    ## Delete a todo by its id

    ### Args:
    - **todo_id**: The id of the todo to delete

    ### Raises:
    - **400**: If there is an issue with the database query
    - **404**: If the todo with the given id is not found
    
    ### Returns:
    - **dict[str, str]**: The deleted todo
    """
    query = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user["id"])
    if not query.first():
        raise HTTPException(status_code=404, detail="Todo not found")
    try:
        deleted_todo = query.first()
        db.delete(deleted_todo)
        db.commit()
        return deleted_todo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
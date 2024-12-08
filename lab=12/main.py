from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# task 1. API. Nikita Polovykh 107б1
app = FastAPI()

class User(BaseModel):
	index: int
	name: str
	role: str

users = {}

@app.get("/")
def read_root():
	return {"message": "Hello world!"}

@app.post("/user")
def create_user(user: User):
	if user.index in users:
		raise HTTPException(status_code=400, detail="Index already exists")
	users[user.index] = user
	return user

@app.get("/user")
def get_users():
	return list(users.values())

@app.get("/user/{id}")
def get_user(id: int):
	if id not in users:
		raise HTTPException(status_code=404, detail="User not found")
	return users[id]

@app.delete("/user/{id}")
def delete_user(id: int):
	if id not in users:
		raise HTTPException(status_code=404, detail="User not found")
	del users[id]
	return {"detail": "User deleted"}
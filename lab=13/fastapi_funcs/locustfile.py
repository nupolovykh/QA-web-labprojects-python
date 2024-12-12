from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 2)

    @task(1)
    def get_root(self):
        self.client.get("/")

    @task(2)
    def create_user(self):
        self.client.post("/user", json={"index": 1, "name": "Alice", "role": "admin"})

    @task(3)
    def get_users(self):
        self.client.get("/user")

    @task(4)
    def get_user(self):
        self.client.get("/user/1")

    @task(5)
    def delete_user(self):
        self.client.delete("/user/1")
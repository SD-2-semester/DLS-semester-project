from locust import HttpUser, task, between
import uuid


class UserBehavior(HttpUser):

    #     @task
    #     def register(self):
    #         unique_email = f"test_{uuid.uuid4()}@test.dk"
    #         unique_username = f"Martin_{uuid.uuid4()}"
    #         payload = {
    #             "email": unique_email,
    #             "password": "string",
    #             "username": unique_username,
    #         }
    #         self.client.post("/auth/api/v1/auth/register", json=payload)

    @task
    def register_rust(self):
        unique_username = f"Martin_{uuid.uuid4()}"
        payload = {
            "user_id": str(uuid.uuid4()),
            "user_name": unique_username,
        }
        self.client.post("/relation/api/v1/user", json=payload)

from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # seconds between tasks

    @task
    def load_home(self):
        self.client.get("/")   # test homepage

    @task
    def search_jobs(self):
        self.client.get("/api/owners/")  # test job search

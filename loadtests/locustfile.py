from locust import HttpUser, task, between


class OrderAllocationUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def allocate_order(self):
        payload = {
            "sku_id": 1,
            "quantity": 1,
            "delivery_latitude": -6.4025,
            "delivery_longitude": 106.7942,
        }
        self.client.post("/v1/orders/allocate", json=payload)
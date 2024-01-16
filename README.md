# Eventchimp
Eventchimp is event scheduling application. It help users to create, organize, and manage events.
This app provide platform where event hosts can customize details, set available time slots.
Attendees, on the other hand, can booking their preferred slots.

# Try it out
**Backend is hosted on:** [https://eventchimp.notlocalhost.space/](https://eventchimp.notlocalhost.space/api-auth/login)

**API Doc (Auto-generated using OpenAPI schema):** [https://eventchimp.notlocalhost.space/api-doc/](https://eventchimp.notlocalhost.space/api-doc/)

# How to run this locally
1. Install docker. https://docs.docker.com/engine/install/
2. Install docker-compose
3. Create .env file in ./src directory with the following vars.
```
DJANGO_SECRET_KEY=sample_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://eventchimp_web:******@localhost:5442/eventchimp_dev

POSTGRES_DB=eventchimp_dev
POSTGRES_USER=eventchimp_web
POSTGRES_PASSWORD==*****
```
4. Run the following command to start the Docker containers:

    ```bash
    docker-compose up
    ```

5. Use the following command to get the container ID of `eventchimp_be:v1`:

    ```bash
    docker ps
    ```

6. Run the following command to enter the Docker container using the obtained container ID:

    ```bash
    docker exec -it :your-container-id: /bin/bash
    ```

7. Inside the container, run the following command to create a superuser:

    ```bash
    /opt/venv/bin/python manage.py createsuperuser
    ```

8. Now, navigate to [http://localhost:8001/schedule-service/api/](http://localhost:8001/schedule-service/api/).

6. The Login button will be visible on the top right side of the navigation. Use the user credentials created in step 7 to log in.

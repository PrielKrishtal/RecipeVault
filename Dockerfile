# Step 1: Set the base image
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the entire project structure
COPY . .

# Step 5: Expose port
EXPOSE 8000

# Step 6: Fix the CMD - use the correct module path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
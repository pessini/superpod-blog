FROM node:25.2.1-slim

# Install OpenSSL and CA certificates required by Prisma
RUN apt-get update -y && apt-get install -y openssl ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the datalayer folder contents
COPY datalayer/ .

# Prisma 7 introduced a breaking change where database connection URLs 
#   are no longer allowed in the schema.prisma file.
# Install Prisma 6 specifically to maintain schema compatibility
RUN npm install -g prisma@6

# Wait for DB to be ready and run migration
ENTRYPOINT [ "sh", "-c", "sleep 5 && npx prisma migrate deploy" ]
# Get all products
curl http://localhost:4000/api/products

# Get single product
curl http://localhost:4000/api/products/1

# Create product (requires authentication)
curl -X POST http://localhost:4000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"New Product","price":99.99}'

# Update product (requires authentication)
curl -X PUT http://localhost:4000/api/products/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"price":89.99}'

# Delete product (requires authentication)
curl -X DELETE http://localhost:4000/api/products/1 \
  -H "Authorization: Bearer YOUR_TOKEN"

curl http://localhost:4000/health # CopIt

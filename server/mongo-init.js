db = db.getSiblingDB('ecommerce');

db.createUser({
  user: 'ecommerce_user',
  pwd: process.env.MONGO_USER_PASSWORD || 'ecommerce_password',
  roles: [
    {
      role: 'readWrite',
      db: 'ecommerce'
    }
  ]
});

// Create collections
db.createCollection('users');
db.createCollection('products');
db.createCollection('orders');

// Create indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.products.createIndex({ name: 1 });
db.products.createIndex({ category: 1 });
db.orders.createIndex({ userId: 1 });
db.orders.createIndex({ createdAt: -1 }); 
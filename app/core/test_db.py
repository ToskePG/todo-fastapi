from app.core.database import engine
 
try:
    connection = engine.connect()
    print("DB connected!")
except Exception as e:
    print("Error: ", e) 
from app import create_app
from app.function_impl.insert_cocktailData import insert_cocktail

app=create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)







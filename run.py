import asyncio
from app import create_app  # Import the function, not the app instance


import uvicorn

async def main():
    app = await create_app()  # Await here

    uvicorn.run(app, host="0.0.0.0", port=80, reload=True, factory=True)

if __name__ == "__main__":
    asyncio.run(main())  # Run the async function

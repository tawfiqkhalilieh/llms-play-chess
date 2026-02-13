
import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    from mcp_server.main import app, startup_event
    import asyncio
    
    print("Successfully imported app.")
    
    # Run startup event
    async def run_startup():
        print("Running startup event...")
        await startup_event()
        print("Startup event complete.")
        
    asyncio.run(run_startup())

except Exception as e:
    print(f"Error during startup check: {e}")
    import traceback
    traceback.print_exc()

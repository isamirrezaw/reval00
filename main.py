from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from instagrapi import Client
import uvicorn

app = FastAPI(title="Instagram AI Relay Server")
cl = Client()

class LoginRequest(BaseModel):
    session_id: str

class SendMessageRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

@app.get("/")
def home():
    return {"status": "online", "message": "Instagram Relay Bridge is Running!"}

@app.post("/api/account-info")
def get_account_info(req: LoginRequest):
    try:
        cl.login_by_sessionid(req.session_id)
        user_info = cl.account_info()
        return {
            "status": "success",
            "username": user_info.username,
            "full_name": user_info.full_name,
            "followers": user_info.follower_count,
            "following": user_info.following_count,
            "profile_pic": str(user_info.profile_pic_url)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instagram Connection Error: {str(e)}")

@app.post("/api/get-directs")
def get_direct_threads(req: LoginRequest):
    try:
        cl.login_by_sessionid(req.session_id)
        threads = cl.direct_threads(amount=10)
        result = []
        for t in threads:
            last_msg = t.messages[0].text if t.messages else ""
            result.append({
                "thread_id": t.id,
                "user_id": str(t.users[0].pk) if t.users else "",
                "username": t.users[0].username if t.users else "Unknown",
                "last_message": last_msg
            })
        return {"status": "success", "threads": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/send-direct")
def send_direct_message(req: SendMessageRequest):
    try:
        cl.login_by_sessionid(req.session_id)
        cl.direct_send(req.message, user_ids=[int(req.user_id)])
        return {"status": "success", "message": "Direct message sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import os
from datetime import datetime
from typing import List
import uvicorn

app = FastAPI(title="CallMate AI Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/callmate_demo_live.html")

@app.get("/callmate_demo_live.html")
async def demo():
    return FileResponse("static/callmate_demo_live.html")

SAMPLE_TRANSCRIPT = [
    {"role": "system", "text": "📞 Çağrı başladı..."},
    {"role": "customer", "text": "Merhaba, faturamda bir sorun var"},
    {"role": "operator", "text": "Merhaba! Size nasıl yardımcı olabilirim?"},
    {"role": "customer", "text": "Geçen ay fazla ücret kesildi"},
    {"role": "operator", "text": "Anlaşıldı, hesabınızı hemen kontrol ediyorum"},
    {"role": "system", "text": "🧠 Müşteri Profili: Sabırsız, Detay Odaklı"},
    {"role": "system", "text": "💡 Tavsiye: Hızlı çözüm sunun, kısa cümleler kullanın"},
    {"role": "customer", "text": "Ne kadar sürer? Hızlı çözmesi lazım"},
    {"role": "operator", "text": "En fazla 2 dakika içinde hallettiriyorum"},
    {"role": "system", "text": "✓ Stres Seviyesi: %45 → Müşteri sinirli ama iyileşiyor"},
    {"role": "operator", "text": "Buldum! Hatalı bir işlem var, iade yapıyorum"},
    {"role": "customer", "text": "Harika! Bunu duymak istiyordum"},
    {"role": "system", "text": "🎉 Müşteri Memnuniyeti: Yüksek!"},
    {"role": "operator", "text": "Bu ay promosyonumuz var, ilgilenebilir misiniz?"},
    {"role": "customer", "text": "Evet, detay al"},
    {"role": "system", "text": "✓ Satış Başarısı: Yüksek! Demo Tamamlandı"},
]

PERSONALITY_TRAITS = ["Sabırsız", "Detay Odaklı", "Hızlı Karar", "Analitik", "Sosyal"]

RECOMMENDATIONS = [
    "Kısa cümlelerle hızlı çözüm sunun",
    "Müşterinin sabrını dinleyin",
    "Somut adımlar önerin",
    "Müşteri sinirli, tonu sakinleştirin",
    "Satış fırsatı: müşteri açık",
    "Detaylı açıklama yapın, puan artar",
]

CUSTOMERS = [
    {"name": "Ayşe Yılmaz", "phone": "0532 XXX XXXX", "prev_purchases": 3, "segment": "VIP"},
    {"name": "Mehmet Kaya", "phone": "0533 XXX XXXX", "prev_purchases": 1, "segment": "Regular"},
    {"name": "Fatma Şahin", "phone": "0534 XXX XXXX", "prev_purchases": 5, "segment": "Premium"},
]

@app.get("/api/health")
async def health_check():
    return {"status": "online", "timestamp": datetime.now().isoformat()}

@app.get("/api/customer/random")
async def get_random_customer():
    customer = random.choice(CUSTOMERS)
    return {
        "name": customer["name"],
        "phone": customer["phone"],
        "prev_purchases": customer["prev_purchases"],
        "segment": customer["segment"],
        "call_time": datetime.now().isoformat()
    }

@app.get("/api/demo/metrics")
async def get_demo_metrics():
    return {
        "stt_accuracy": 92 + random.randint(-3, 2),
        "stress_level": random.randint(30, 60),
        "satisfaction": random.randint(6, 10),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/demo/emotions")
async def get_demo_emotions():
    happy = random.randint(20, 50)
    neutral = random.randint(30, 50)
    angry = 100 - happy - neutral
    return {
        "happy": max(0, happy),
        "neutral": max(0, neutral),
        "angry": max(0, angry)
    }

@app.get("/api/demo/personality")
async def get_demo_personality():
    return {
        "traits": random.sample(PERSONALITY_TRAITS, k=3),
        "confidence": random.randint(75, 95)
    }

@app.get("/api/demo/recommendations")
async def get_demo_recommendations():
    return {"recommendations": random.sample(RECOMMENDATIONS, k=3)}

@app.post("/api/demo/start")
async def start_demo():
    return {
        "demo_id": f"DEMO_{datetime.now().timestamp()}",
        "status": "started",
        "message": "Demo başladı"
    }

@app.post("/api/demo/end")
async def end_demo():
    return {
        "status": "ended",
        "final_metrics": {
            "total_duration": random.randint(60, 300),
            "customer_satisfaction": random.randint(7, 10),
            "operator_performance": random.randint(7, 10),
            "sales_success": random.randint(50, 95)
        }
    }

@app.websocket("/ws/call/{call_id}")
async def websocket_call_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    try:
        await websocket.send_json({
            "type": "connection",
            "message": f"Connected to call {call_id}"
        })

        for i, line in enumerate(SAMPLE_TRANSCRIPT):
            await asyncio.sleep(0.8)

            await websocket.send_json({
                "type": "transcript",
                "line": line,
                "index": i
            })

            if i % 3 == 0:
                await websocket.send_json({
                    "type": "metrics",
                    "data": {
                        "stt_accuracy": 92 + random.randint(-2, 2),
                        "stress_level": 45 + random.randint(-10, 10),
                        "satisfaction": round((i / len(SAMPLE_TRANSCRIPT)) * 10, 1)
                    }
                })

            if i % 4 == 0:
                happy = max(0, 40 - random.randint(5, 15))
                angry = random.randint(10, 35)
                neutral = 100 - happy - angry
                await websocket.send_json({
                    "type": "emotions",
                    "data": {"happy": happy, "neutral": neutral, "angry": angry}
                })

        await websocket.send_json({
            "type": "personality",
            "data": {
                "traits": random.sample(PERSONALITY_TRAITS, k=3)
            }
        })

        await websocket.send_json({
            "type": "recommendations",
            "data": {
                "recommendations": random.sample(RECOMMENDATIONS, k=3)
            }
        })

        await websocket.send_json({
            "type": "complete",
            "message": "Demo tamamlandı",
            "final_score": random.randint(7, 10)
        })

    except WebSocketDisconnect:
        print(f"Client disconnected: {call_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    print("🚀 CallMate AI Demo API başlatılıyor...")
    print("📍 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
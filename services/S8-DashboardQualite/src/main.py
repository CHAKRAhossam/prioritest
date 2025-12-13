"""
Service 8 - Dashboard Qualité
Point d'entrée aligné avec les spécifications d'architecture.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
from datetime import datetime

app = FastAPI(
    title="Dashboard Qualité API",
    description="""
    Interface web pour visualiser recommandations, couverture, risques, tendances.
    
    ## Fonctionnalités
    
    * **REST API** : Endpoints pour récupérer les données consolidées
    * **WebSocket** : Communication temps réel pour mises à jour
    * **Visualisations** : Recommandations, couverture, risques, tendances
    * **Exports** : PDF/CSV pour rapports
    
    Aligned with architecture specification.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "DashboardQualite"}


@app.get("/api/v1/dashboard/overview")
def get_overview(repository_id: str):
    """
    Get dashboard overview aligned with architecture specification.
    
    GET /api/v1/dashboard/overview?repository_id=repo_12345
    
    Response format from architecture spec:
    {
      "repository_id": "repo_12345",
      "summary": {
        "total_classes": 150,
        "classes_with_tests": 120,
        "average_coverage": 0.78,
        "high_risk_classes": 15,
        "recommended_classes": 20
      },
      "recommendations": [...],
      "coverage_trends": [...],
      "risk_distribution": [...],
      "impact_metrics": {
        "defects_prevented": 12,
        "time_saved_hours": 45,
        "coverage_gain": 0.15
      }
    }
    """
    # Placeholder - would fetch from S3, S5, S6
    return {
        "repository_id": repository_id,
        "summary": {
            "total_classes": 150,
            "classes_with_tests": 120,
            "average_coverage": 0.78,
            "high_risk_classes": 15,
            "recommended_classes": 20
        },
        "recommendations": [],
        "coverage_trends": [],
        "risk_distribution": [],
        "impact_metrics": {
            "defects_prevented": 12,
            "time_saved_hours": 45,
            "coverage_gain": 0.15
        }
    }


@app.get("/api/v1/dashboard/export")
def export_dashboard(format: str = "pdf", repository_id: str = None):
    """
    Export dashboard data aligned with architecture specification.
    
    GET /api/v1/dashboard/export?format=pdf&repository_id=repo_12345
    """
    # Placeholder - would generate PDF/CSV
    return {"status": "exported", "format": format, "repository_id": repository_id}


@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates aligned with architecture specification.
    
    WebSocket /ws/dashboard
    
    Message format from architecture spec:
    {
      "event_type": "coverage_update|risk_update|recommendation_update",
      "data": {
        "repository_id": "repo_12345",
        "class_name": "com.example.UserService",
        "current_coverage": 0.85,
        "risk_score": 0.75,
        "recommendation_priority": 1
      },
      "timestamp": "2025-12-04T11:05:00Z"
    }
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            # Echo back (in real implementation, would process and broadcast)
            await websocket.send_json({
                "event_type": "ack",
                "data": {"message": "Received"},
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)


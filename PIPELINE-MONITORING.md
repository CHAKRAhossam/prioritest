# PRIORITEST Pipeline Monitoring Guide

## ✅ Current Status: ALL SERVICES RUNNING

All services (S1-S7) are up and healthy!

## 🚀 How to Trigger a Pipeline Run

1. **Open Dashboard**: http://localhost:3000
2. **Click "Add Repository"**
3. **Enter GitHub URL**: e.g., `https://github.com/spring-projects/spring-petclinic`
4. **Pipeline starts automatically!**

## 📊 Pipeline Flow (S1 → S2 → S4 → S5 → S6)

```
S1 (Collection)
  ↓ Collects commits → Publishes to Kafka
S2 (Static Analysis) 
  ↓ Automatically processes Kafka events
S4 (Preprocessing)
  ↓ Prepares features
S5 (ML Predictions)
  ↓ Generates risk predictions
S6 (Prioritization)
  ↓ Creates prioritized test plan
S7 (Test Scaffolding) - Optional
  ↓ Generates test code
```

## 🔍 How to Monitor Pipeline

### Quick Status Check
```powershell
.\scripts\check-pipeline-status.ps1
```

### Watch S1 Logs (Orchestration)
```powershell
docker logs prioritest-collecte-depots -f
```
Look for:
- "Starting full analysis pipeline for..."
- "Step 1: Collecting commits..."
- "Step 2: Waiting for S2..."
- "Step 3: Triggering S4..."
- "Step 4: Triggering S5..."
- "Step 5: Triggering S6..."

### Watch All Services
```powershell
docker-compose logs -f
```

### Watch Specific Service
```powershell
# S2 (Static Analysis)
docker logs prioritest-analyse-statique -f

# S4 (Preprocessing)
docker logs prioritest-pretraitement-features -f

# S5 (ML Predictions)
docker logs prioritest-ml-service -f

# S6 (Prioritization)
docker logs prioritest-moteur-priorisation -f
```

### Monitor Specific Repository
```powershell
.\scripts\monitor-pipeline.ps1 -RepositoryId 'github_spring-projects_spring-graphql' -Follow
```

## 🏥 Health Check Endpoints

- **S1**: http://localhost:8001/health
- **S2**: http://localhost:8081/actuator/health
- **S3**: http://localhost:8082/actuator/health
- **S4**: http://localhost:8000/health
- **S5**: http://localhost:8001/health
- **S6**: http://localhost:8006/health
- **S7**: http://localhost:8007/health
- **API Gateway**: http://localhost:8090/actuator/health

## 📝 What to Look For in Logs

### S1 (Collection)
- "Starting full analysis pipeline"
- "Step 1: Collecting commits"
- "Step 2: Waiting for S2"
- "Step 3: Triggering S4"
- "Step 4: Triggering S5"
- "Step 5: Triggering S6"
- "Full analysis pipeline completed"

### S2 (Static Analysis)
- "Processing commit"
- "Analyzed"
- "Metrics calculated"

### S4 (Preprocessing)
- "Preprocessing"
- "Features prepared"
- "completed"

### S5 (ML Predictions)
- "Predictions"
- "Batch prediction"
- "completed"

### S6 (Prioritization)
- "Prioritization"
- "prioritized"
- "completed"

## ⚠️ Common Issues

### No Pipeline Activity
- Check if repository was added in dashboard
- Verify S1 logs for "Starting full analysis pipeline"
- Check API Gateway is accessible (port 8090)

### Pipeline Stuck
- Check S2 is processing Kafka events
- Verify S4, S5, S6 are running
- Check service health endpoints

### Predictions Not Found
- Wait 1-2 minutes for pipeline to complete
- S2 needs time to analyze commits
- S4 and S5 must complete before S6

## 🎯 Quick Commands Reference

```powershell
# Check all services status
.\scripts\check-pipeline-status.ps1

# Monitor pipeline for specific repo
.\scripts\monitor-pipeline.ps1 -RepositoryId 'repo_id' -Follow

# View all logs
docker-compose logs -f

# View S1 logs
docker logs prioritest-collecte-depots -f

# Restart all services
docker-compose restart

# Check container status
docker ps --filter "name=prioritest"
```


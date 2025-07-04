# F1 Predict Pro - Deployment Guide

This guide provides multiple deployment options for the F1 Predict Pro API, maintaining full ML functionality without removing any original code.

## Option 1: Railway (Recommended for Full ML Functionality)

Railway supports Docker deployments and can handle heavy ML dependencies like pandas, numpy, and scikit-learn.

### Steps:

1. **Create Railway Account**: Sign up at [railway.app](https://railway.app)

2. **Connect GitHub Repository**: 
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your f1predictpro repository

3. **Configure Environment Variables** (if needed):
   ```
   PYTHONPATH=/app
   PORT=8000
   ```

4. **Deploy**: Railway will automatically detect the `Dockerfile` and `railway.json` configuration

5. **Access Your API**: Railway will provide a public URL like `https://your-app.railway.app`

### Benefits:
- Full ML functionality with pandas, numpy, scikit-learn
- Docker-based deployment handles all dependencies
- Automatic scaling and monitoring
- Free tier available

## Option 2: Vercel (Lightweight with Optimized Dependencies)

Vercel deployment using pre-compiled wheels for better compatibility.

### Steps:

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   cd f1predictpro
   vercel
   ```

3. **Configuration**: The `vercel.json` file is already configured with:
   - Optimized Python runtime
   - Pre-compiled wheels for ML libraries
   - Increased memory and timeout limits

### Benefits:
- Fast deployment
- Global CDN
- Automatic HTTPS
- Good for development/testing

### Limitations:
- May have issues with complex ML dependencies
- Limited to serverless functions

## Option 3: Docker Local/Cloud Deployment

For full control and guaranteed compatibility.

### Local Docker:
```bash
# Build the image
docker build -t f1predictpro .

# Run the container
docker run -p 8000:8000 f1predictpro
```

### Cloud Deployment:
- **Google Cloud Run**: Deploy the Docker image
- **AWS ECS/Fargate**: Container-based deployment
- **Azure Container Instances**: Simple container deployment

## Testing Your Deployment

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-domain.com/api/health

# Get predictions
curl https://your-domain.com/api/predictions

# Get betting recommendations
curl https://your-domain.com/api/betting/recommendations
```

## Troubleshooting

### Vercel Issues:
- If you get dependency errors, the optimized `requirements-vercel.txt` should resolve them
- Check Vercel function logs for specific error messages

### Railway Issues:
- Check build logs in Railway dashboard
- Ensure Dockerfile is in the root directory

### General Issues:
- Verify all required files are committed to Git
- Check that environment variables are set correctly
- Ensure the API server starts without errors locally first

## Recommendation

For production use with full ML functionality, **Railway is recommended** as it provides:
- Complete compatibility with all ML dependencies
- Docker-based deployment for consistency
- Easy scaling and monitoring
- Reliable performance for ML workloads

Vercel can be used for development/testing but may have limitations with heavy ML dependencies.
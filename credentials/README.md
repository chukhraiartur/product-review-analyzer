# Google Cloud Credentials

## 📁 Place your GCP credentials file here

1. **Download your service account key** from Google Cloud Console:
   - Go to IAM & Admin → Service Accounts
   - Click on your service account
   - Go to Keys tab → Add Key → Create New Key
   - Choose JSON format and download

2. **Rename the file** to `gcp-credentials.json`

3. **Place it in this folder** (`credentials/gcp-credentials.json`)

## 🔒 Security Notes

- ✅ This folder is in `.gitignore` - credentials will NOT be committed
- ✅ Keep your credentials file secure
- ✅ Never share or commit your credentials
- ✅ Each user should have their own credentials file

## 📝 Example file structure

```
credentials/
├── README.md
└── gcp-credentials.json  # Your credentials file here
```

## 🚨 Important

The application expects the file to be named `gcp-credentials.json`. 
If your downloaded file has a different name, please rename it. 
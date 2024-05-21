# NxtBn's Square Payment Link Plugin


NxtBn's Stripe Payment Link Plugin can be installed in NxtBn Ecom in two ways: one is via the NxtBn dashboard panel and another is manually by modifying the codebase.

## Installation

### Via NxtBn Dashboard

1. Go to the Plugins section in the dashboard: `Plugins > Upload Plugin`.
2. During the upload, select the plugin category as `"payment_processor"`.

### Manually

1. Download or clone this project.
2. Place the files in your NxtBn codebase at this location: `nxtbn/payment/plugin/`.

That's it! The plugin will automatically be recognized by the system.

## Configuration

The Square Payment Link Plugin requires the following environment variables to be set:

- `SQUARE_API_URL=`
- `SQUARE_VERSION=`
- `SQUARE_ACCESS_TOKEN=`
- `SQUARE_LOCATION_ID=`
- `SQUARE_WEBHOOK_SIGNATURE_KEY=`

### Updating .env Variables

You can update these variables either via the NxtBn dashboard under `Settings` or directly in the codebase using:
```bash
nano .env
```

# Obtaining Square API Keys
To fully integrate the Square Payment Link Plugin with your NxtBn Ecom platform, you need to obtain a few specific API keys from Square: the Secret Key and the Webhook Key. Here's how you can retrieve these keys:

## Create a Square Developer Account

To start using the Square APIs, you need to create a Square Developer account.

1. **Sign Up or Log In**
   - Go to the [Square Developer Portal](https://developer.squareup.com/).
   - If you don’t have a Square account, click on “Sign Up” and follow the prompts to create an account.
   - If you already have a Square account, click “Log In” and enter your credentials.

2. **Create a Developer Account**
   - After logging in, you will be redirected to the Square Developer Dashboard.
   - Click on “New Application” to create a new app.
   - Enter a name for your application and click “Create Application”.

## Obtain API Credentials

Once you have created a developer account and an application, you can obtain the necessary API credentials.

### SQUARE_API_URL

The base URL for Square's API is consistent across different applications:


### SQUARE_VERSION
 Square API versions are date-based, and you need to specify the version you are using in your API requests. You can find the latest version in the Square API documentation.

### SQUARE_ACCESS_TOKEN
- In the Square Developer Dashboard, select your application.
- Go to the "Credentials" tab.
- Under the "Access Tokens" section, click on "Generate Token" for the environment (Sandbox or Production) you are working in.
- Copy the generated access token and store it securely.

### SQUARE_LOCATION_ID
- The location ID is required for many API requests.

  
### SQUARE_WEBHOOK_SIGNATURE_KEY
- In the Square Developer Dashboard, select your application.
- Go to the "Webhooks" tab and click "Create Webhook".
- Provide the URL where you want to receive webhook events and select the events you want to subscribe to.
- After creating the webhook, you will see the "Signature Key" in the webhook details.
- Copy the signature key and store it securely.

 Ensure you store these keys securely and only in your environment variables to protect sensitive information.

# ML-URL-Category

Welcome to ML-URL-Category, a cutting-edge web content classification service tailored to enhance online safety for children. It incorporates two machine learning models: xlm-roberta-base and tinybert. The service has processed the top 5 million websites using a fine-tuned version of the xlm-roberta-large model for accurate classification. Tinybert, optimized for efficiency, has been fine-tuned on the same dataset, quantized, and converted to ONNX format for lightweight deployment and fast performance.

Our database includes classifications for 5 million websites, meticulously stored in a MariaDB database, with Redis employed to optimize data retrieval through effective caching. The classifier is adept at distinguishing among 17 nuanced categories, ensuring a broad spectrum of internet content is accurately identified and categorized.

Classifier has 17 classes:

```
1. safe
2. body_image/related_to_disordered_eating
3. clothing_fashion_and_jewelry
4. criminal/malicious
5. drugs_alcohol_or_tobacco_related
6. entertainment_news_and_streaming
7. fake_news
8. gambling
9. hate_speech
10. online_gaming
11. self_harm/suicidal_content
12. sex_education
13. shopping_and_product_reviews
14. social_media_and_chat
15. violence
16. weapons
17. adult_sexual_content
```

This project is fully open-source. If you want to test it and download models, training data or raw 5m website data, follow instructions below.

## How to Test with UI

You will need AWS CLI installed on your computer for `setup.sh` to work.

### Instructions for Installing AWS CLI:

#### Windows:

1. **Download the AWS CLI MSI Installer for Windows** (64-bit or 32-bit) from the [AWS CLI official page](https://aws.amazon.com/cli/).
2. **Run the downloaded MSI installer** and follow the on-screen instructions.
3. **Verify the installation** by opening the Command Prompt and running `aws --version`.

#### Linux:

1. Download and install using the bundled installer with the following command:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### macOS:

```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

After installing AWS CLI, open the terminal and run:

```bash
bash setup.sh
```

This will download 5M URLs for MariaDB and a tiny model for inferring new websites. You can use `--large-model` flag for downloading a larger and better quality model and `--parsed-data` to download raw training (136K) and 5M URLs data. These are optional and are not needed for basic usage of the service.

Then, navigate to the web application directory:

```bash
cd web_app
docker-compose up
```

Note: The `.env` is pushed on the repo. This practice is not encouraged, but this is just a demonstration of how you can store sensitive information in your project. **Do not forget to uncomment `.env` in `.gitignore`**.

Finally, open http://localhost:8000/ in your browser to access the application.

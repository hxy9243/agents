# Anyscale Company Report

## Overview

Anyscale, founded in 2019 by Ion Stoica, Robert Nishihara, and Philipp Moritz, is headquartered in San Francisco, CA. The company's mission is to make scalable computing effortless, with a vision to build the future of distributed computing for AI and ML workflows ([https://www.anyscale.com/about-us](https://www.anyscale.com/about-us)). Keerti Melkote was appointed CEO in July 2024 ([https://www.anyscale.com/press/anyscale-names-industry-veteran-keerti-melkote-chief-executive-officer](https://www.anyscale.com/press/anyscale-names-industry-veteran-keerti-melkote-chief-executive-officer)).

## Products

Anyscale offers a unified AI platform designed for rapid and cost-efficient AI/ML production ([https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform)). Key features include:

*   **RayTurbo:** Anyscale’s optimized engine for Ray, offering significant performance improvements. It can be up to 4.5x faster for read-intensive data workloads and LLM scaling, and up to 6.1x cheaper for LLM batch inference. It also reduces costs through spot instance and elastic training ([https://www.anyscale.com/platform/rayturbo](https://www.anyscale.com/platform/rayturbo)).
*   **Integrated Developer Tools:** Simplified environment with VSCode and Jupyter notebook integrations, automated dependency management, and app accelerators ([https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform)).
*   **Resource Management:** Unified compute pool with flexible deployment options, including public cloud, on-prem, and Kubernetes clusters ([https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform)).
*   **Reliable Production Services:** Includes Anyscale Jobs for batch workload management and Anyscale Services for code deployment with high availability and zero downtime upgrades ([https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform)).
*   **Compute Governance:** Security and access control with secure log management, user access controls, cost tracking, and SOC 2 Type II attestation ([https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform)).

Anyscale simplifies ML model deployment with Ray Serve, offering support for various model serving patterns, reliability, advanced observability, and optimized resource scheduling ([https://www.anyscale.com/use-case/model-serving-deployment](https://www.anyscale.com/use-case/model-serving-deployment)). Key features include fast node launching, autoscaling, multi-AZ support, zero downtime upgrades, spot instance support, model multiplexing, dynamic batching, and support for large model parallelism.

Choosing Anyscale provides boosted developer productivity, lower total cost of ownership, and access to Ray experts ([https://www.anyscale.com/product](https://www.anyscale.com/product)). Anyscale builds on open-source Ray with RayTurbo, interactive notebooks, enterprise governance, and seamless integrations ([https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io](https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io)).

## Technology Stack

Anyscale is a configurable AI platform designed for rapid and cost-effective production deployment of AI applications ([https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform)).

Anyscale's technology stack leverages several key components:

*   **Ray:** An AI compute engine for scaling AI and Python applications ([https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io](https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io)).
*   **RayTurbo:** Anyscale’s optimized engine for Ray, enhancing performance, scale, efficiency, and reliability ([https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io](https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io), [https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform), [https://www.anyscale.com/platform/rayturbo](https://www.anyscale.com/platform/rayturbo)).
*   **Kubernetes:** A container orchestrator for resource management ([https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm)).
*   **PyTorch:** A dominant deep learning framework ([https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm)).
*   **vLLM:** An inference engine specialized for transformers ([https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm)).

A common architecture involves **Kubernetes + Ray + PyTorch + vLLM** ([https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm)).

Anyscale provides several advantages over open-source Ray:

*   **Improved Performance:** RayTurbo offers up to 4.5x faster performance for read-intensive workloads ([https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io](https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io)).
*   **Lower Costs:** Up to 6x cheaper for LLM batch inference compared to AWS Bedrock and OpenAI, and up to 60% lower costs on various workloads ([https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io](https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io), [https://www.anyscale.com/platform/rayturbo](https://www.anyscale.com/platform/rayturbo)).
*   **Better Reliability:** Includes features like head node support, on-demand fallback, zero downtime upgrades, and memory limits ([https://www.anyscale.com/platform/rayturbo](https://www.anyscale.com/platform/rayturbo)).
*   **Higher QPS:** Up to 60% higher QPS serving with optimized Ray Serve ([https://www.anyscale.com/platform/rayturbo](https://www.anyscale.com/platform/rayturbo)).
*   **Faster Time to Market:** Customers like Canva report up to 12X faster iteration ([https://www.anyscale.com/product/platform](https://www.anyscale.com/product/platform)).

## Customer Success Stories

*   **Blue River Technology:**
    *   Challenge: Regression testing was time-consuming.
    *   Solution: Migrated AI workload processing to Ray, managed by Anyscale, on AWS.
    *   Impact: Regression testing sped up by more than 2x, increasing engineering team productivity by 2.5x. Improved resource efficiency through shared hardware. Enhanced reliability with automatic job retries and notifications. Fail-safe operations due to the AWS cluster removing single points of failure. ([Blue River Technology Developers Iterate 2.5x Faster to Empower Farmers](https://www.anyscale.com/resources/case-study/blue-river-technology))
*   **Canva:**
    *   Challenge: Scaling its prior solution was challenging and inefficient.
    *   Solution: Implemented an AI platform using Anyscale.
    *   Impact: Up to 12x faster innovation velocity, with image classification training 12x faster. Improved hardware efficiency, with GPUs now fully saturated at peak load. ([How Canva Reduced AI Costs by 50% with Anyscale](https://www.anyscale.com/resources/case-study/how-canva-built-a-modern-ai-platform-using-anyscale))
*   **SewerAI:**
    *   Challenge: Processing large data volumes led to bottlenecks and low GPU utilization (25%).
    *   Solution: Utilized Anyscale’s Workspaces feature to build distributed Ray applications.
    *   Impact: 3x faster batch inference. 50% reduction in required machines and 95% GPU utilization. Nearly instantaneous code testing. Over 75% reduction in total cost of ownership (TCO) compared to AWS Batch. ([How SewerAI Saved 75% in Cloud Operating Costs](https://www.anyscale.com/resources/case-study/sewerai))
*   **Attentive:**
    *   Challenge: Scaling compute became a bottleneck, with significant time spent managing infrastructure.
    *   Solution: Chose Anyscale as their AI Compute Platform and Ray as their AI Compute Engine.
    *   Impact: 99% reduction in cost. Able to process 12x more data. 5x reduction in training time. 50x increase in the number of customers supported by models. Scaled training from millions to billions of data points. ([Attentive Revolutionizes Personalized Marketing with Anyscale](https://www.anyscale.com/resources/case-study/attentive))
*   **Handshake:**
    *   Challenge: Needed to quickly match millions of individuals with jobs; faced hurdles with AI platform capabilities and infrastructure.
    *   Solution: Adopted Anyscale to modernize their AI platform, scaling training across multiple GPUs and machines.
    *   Impact: 90% higher engagement on jobs. 5x faster iteration for AI workloads. 50% savings on cloud costs. 10x scalability and >50% cost savings for LLM GPUs. ([How Handshake Saves 50% on LLM GPU Costs with Anyscale](https://www.anyscale.com/resources/case-study/how-handshake-saves-50-on-llm-gpu-costs-with-anyscale))

Over 50,000 developers use Ray ([https://www.anyscale.com/press/anyscale-names-industry-veteran-keerti-melkote-chief-executive-officer](https://www.anyscale.com/press/anyscale-names-industry-veteran-keerti-melkote-chief-executive-officer)). Ray is used by industry leaders such as Uber, OpenAI, Shopify, and Amazon ([https://www.anyscale.com/about](https://www.anyscale.com/about)). Examples of Ray successes include OpenAI using it to train GPT-4, Uber standardizing model training on it, and Amazon processing exabytes of data with it ([https://www.anyscale.com/press/anyscale-names-industry-veteran-keerti-melkote-chief-executive-officer](https://www.anyscale.com/press/anyscale-names-industry-veteran-keerti-melkote-chief-executive-officer)).

## Partnerships

Anyscale has established strategic partnerships to enhance its AI platform:

*   **Google Cloud:** Integration of Anyscale RayTurbo with Google Kubernetes Engine (GKE) creates a unified platform for AI application development and scaling. This partnership boosts task-execution speed and enhances GPU/TPU utilization, leading to optimized performance and higher throughput. [Google Cloud Partnership](https://cloud.google.com/blog/products/containers-kubernetes/partnering-with-anyscale-to-integrate-rayturbo-with-gke)
*   **AWS:** Anyscale is an AWS Partner, providing a managed service for building scalable AI applications on Ray. Customers like Anastasia.ai have seen significant improvements, such as a 9x acceleration of ML processes and an 87% cost reduction. Canva has also benefited, achieving 12x faster model testing and a 50% reduction in cloud costs. [AWS Partnership](https://partners.amazonaws.com/partners/0018a00001mRi2cAAC/Anyscale)
*   **NVIDIA:** Anyscale partners with NVIDIA to improve LLM performance and efficiency on Ray and the Anyscale Platform. The integration of NVIDIA AI software, including TensorRT-LLM, Triton Inference Server, and NeMo, enables parallel model execution, standardized AI model deployment, and an end-to-end framework for generative AI. [NVIDIA Partnership](https://www.anyscale.com/press/anyscale-teams-with-nvidia-to-supercharge-llm-performance-and-efficiency)

The Anyscale Partner program empowers AI teams through technical access & support, marketing initiatives, and sales enablement. [Anyscale Partner Program](https://www.anyscale.com/partners/join)

## Funding

Anyscale was founded in 2019 and has raised a total of $260M over 3 funding rounds ([https://www.cbinsights.com/company/anyscale](https://www.cbinsights.com/company/anyscale)).

*   **Series A ($20.6M):** August 2, 2019. Investors included a16z, Amplify Partners, 11.2 Capital, Nea, The House Fund, and Intel Capital ([https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors](https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors)).
*   **Series B ($40M):** October 21, 2020. The round was led by NEA, with participation from Andreessen Horowitz (a16z), Foundation Capital, and Intel Capital ([https://www.anyscale.com/press/anyscale-announces-usd40m-in-series-b-funding-led-by-nea](https://www.anyscale.com/press/anyscale-announces-usd40m-in-series-b-funding-led-by-nea)).
*   **Series C ($199M):** October 15, 2021. The round was led by a16z and Addition, with participation from New Enterprise Associates, Foundation Capital, and Intel Capital. The post-money valuation was $1B ([https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors](https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors)). Anyscale's valuation reached $1B as of December 9, 2021 ([https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors](https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors)), achieving Unicorn status.

Anyscale has a total of 10 institutional investors including a16z, Addition, New Enterprise Associates, Foundation Capital, Intel Capital, Intel, Amplify Partners, 11.2 Capital, Nea, and The House Fund ([https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors](https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors)).

## Competitors

Anyscale's competitors include a wide range of AI platforms, infrastructure providers, and MLOps tools. Key competitors include:

*   **AI Platforms and Services:** Vertex AI, Amazon SageMaker, Azure AI, Google Cloud AI, IBM watsonx, DataRobot AI Platform, Dataiku, Hugging Face, Together AI, aiXplain, Klu.ai
*   **Infrastructure and Compute Providers:** RunPod, MosaicML, TensorWave, Deep Infra, NVIDIA AI Enterprise, Banana, NVIDIA Triton™, FluidStack, Amazon EC2 Trn2, Google Cloud TPU, Mystic, Prime Intellect
*   **MLOps and Deployment Tools:** BentoML, Seldon, Baseten, ClearML, Wallaroo, Pipeshift
*   **Other Alternatives:** Massdriver, Movestax, Toolhouse, Stacktape, Griptape, Nscale, Spot Ocean, IBM Cloud® Schematics, Shoreline, Argonaut, Allegro.ai, Domino
*   **Tools and Frameworks:** Jupyter Notebook, TensorFlow, KNIME, Anaconda, Posit (formerly RStudio)

Other listed competitors include: Elastic, F(x) Data Labs, HyperScience, Kount, Rasa, OctoML, Fanbank, OWKIN, Geophysical Insights, Iguazio, Aylien, Mind Foundry, Spell, Def-Logix, Obviously AI, Pendo Systems, SVT Robotics, Gamalon, Skyl, Streamlit, Drishti, BenchSci, Cape Privacy, Admit Hub, Saturn Cloud, IBM SPSS Modeler, Oracle Machine Learning, Qlik Sense, Azure Databricks, Intel® Tiber™ AI Studio.

Information Table

| Field | Value |
|---|---|
| Total Raised | $260M |
| Valuation | $1B (Dec 09, 2021) |
| Funding Rounds | Series A, Series B, Series C |
| Investors | Andreessen Horowitz, NEA, Addition, Intel Capital, and Foundation Capital |
| Founded Year | 2019 |
| CEO | Keerti Melkote |
| Founders | Ion Stoica, Robert Nishihara, Philipp Moritz |
| HQ | San Francisco, CA |
| Mission | Make scalable computing effortless |
| Vision | Build the future of distributed computing for AI and ML workflows |
| Product | Anyscale Platform |
| Key Features | RayTurbo optimized runtime, integrated workspace, production jobs, Anyscale services, enterprise security and governance, integrations, expert support and training |
| Benefits | Improved performance, reduced costs, access to new technologies, scalable AI applications |
| Model Serving Features | Fast node launching, autoscaling, multi-AZ support, zero downtime upgrades, spot instance support, model multiplexing, model composition, dynamic batching, fractional resource allocation, large model parallelism |
| Customers | Coinbase, Attentive, Spotify, Uber, Canva, Wildlife Studios, Anastasia.ai |
| Key Technologies | Ray, RayTurbo, Kubernetes, PyTorch, vLLM |
| Use Cases | Data Processing, Model Training, Model Serving, LLM Inference |
| Partners | Google Cloud, AWS, NVIDIA |
| Products | Ray, RayTurbo, Anyscale Platform, Anyscale Endpoints |

# References

## Anyscale funding rounds

- Anyscale Announces $40M in Series B Funding Led by NEA: https://www.anyscale.com/press/anyscale-announces-usd40m-in-series-b-funding-led-by-nea
- 2025 Funding Rounds & List of Investors - Anyscale - Tracxn: https://tracxn.com/d/companies/anyscale/__9qatL-iNLAEZkPcRa1pWyWpgRnkA0yFrWG6KKNOk-9o/funding-and-investors
- Anyscale - Pioneering Scalable Deployment in Generative AI: https://www.mvp.vc/company-initations/initiation-report-anyscale---pioneering-scalable-deployment-in-generative-ai
- Products, Competitors, Financials, Employees, Headquarters Locations: https://www.cbinsights.com/company/anyscale
- How Anyscale hit $111.9M revenue with a 281 person team in 2023.: https://getlatka.com/companies/anyscale.com/funding

## Anyscale leadership team

- Leadership Team - Anyscale - The Org: https://theorg.com/org/anyscale/teams/leadership-team
- About Us - Anyscale: https://www.anyscale.com/about-us
- Anyscale Names Industry Veteran Keerti Melkote Chief Executive ...: https://www.anyscale.com/press/anyscale-names-industry-veteran-keerti-melkote-chief-executive-officer
- Anyscale Management Team - CB Insights: https://www.cbinsights.com/company/anyscale/people
- Anyscale – About Us: https://www.anyscale.com/about

## Anyscale product features

- Unified Compute Platform for AI & Python Apps - Anyscale: https://www.anyscale.com/product/platform
- Fully managed Ray | Anyscale: https://www.anyscale.com/product
- Comparing Ray and Anyscale: https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io
- RayTurbo: Anyscale's Ray Optimized Runtime: https://www.anyscale.com/platform/rayturbo
- Model Deployment and Serving at Scale: https://www.anyscale.com/use-case/model-serving-deployment

## Anyscale customer case studies

- Blue River Technology Developers Iterate 2.5x Faster to Empower ...: https://www.anyscale.com/resources/case-study/blue-river-technology
- How Canva Reduced AI Costs by 50% with Anyscale: https://www.anyscale.com/resources/case-study/how-canva-built-a-modern-ai-platform-using-anyscale
- How SewerAI Saved 75% in Cloud Operating Costs: https://www.anyscale.com/resources/case-study/sewerai
- Attentive Revolutionizes Personalized Marketing with Anyscale: https://www.anyscale.com/resources/case-study/attentive
- How Handshake Saves 50% on LLM GPU Costs with Anyscale: https://www.anyscale.com/resources/case-study/how-handshake-saves-50-on-llm-gpu-costs-with-anyscale

## Anyscale competitors

- Top Anyscale Alternatives in 2025 - Slashdot: https://slashdot.org/software/p/Anyscale/alternatives
- Top Anyscale Alternatives, Competitors - CB Insights: https://www.cbinsights.com/company/anyscale/alternatives-competitors
- Anyscale Alternatives & Competitors | 2025 - Serchen: https://www.serchen.com/company/anyscale/alternatives/
- List of Best Anyscale Alternatives & Competitors 2025 - TrustRadius: https://www.trustradius.com/products/anyscale-unified-compute-platform/competitors
- Anyscale | Supercharge your AI Platform: https://www.anyscale.com/

## Anyscale technology stack

- Anyscale | Supercharge your AI Platform: https://www.anyscale.com/
- Components of an Open Source AI Compute Tech Stack - Anyscale: https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm
- Unified Compute Platform for AI & Python Apps | Anyscale: https://www.anyscale.com/product/platform
- Comparing Ray and Anyscale: https://www.anyscale.com/compare/open-source?utm_campaign=nav&utm_medium=website&utm_source=ray_io
- RayTurbo: Anyscale's Ray Optimized Runtime: https://www.anyscale.com/platform/rayturbo

## Anyscale partnerships

- Partnering with Anyscale to integrate RayTurbo with GKE: https://cloud.google.com/blog/products/containers-kubernetes/partnering-with-anyscale-to-integrate-rayturbo-with-gke
- Become an Anyscale Partner: https://www.anyscale.com/partners/join
- Anyscale - Find an AWS Partner: https://partners.amazonaws.com/partners/0018a00001mRi2cAAC/Anyscale
- Anyscale Teams With NVIDIA to Supercharge LLM Performance and Efficiency: https://www.anyscale.com/press/anyscale-teams-with-nvidia-to-supercharge-llm-performance-and-efficiency
- Anyscale | Supercharge your AI Platform: https://www.anyscale.com/


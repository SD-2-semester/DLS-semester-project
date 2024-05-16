# Run the application

To run the project, you must have docker & docker-compose installed.

## Docker

Run the following command in the root of the project, this will set up everything for you and run the project in development mode.

```bash
docker-compose up --build
```

## Kubernetes

If you want to run the project in Kubernetes, navigate to `kube` folder in the root of the project, and run the following command:
NB! You must have a running cluster the manifests can be applied to.

```bash
kubectl apply -f .
```


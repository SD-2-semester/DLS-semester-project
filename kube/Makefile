run:
	k3d cluster create --api-port 6550 -p "80:80@loadbalancer" my-cluster

destroy:
	k3d cluster delete my-cluster

status:
	kubectl get all

apply:
	kubectl apply -f .

reapply:
	kubectl delete -f .
	kubectl apply -f .
# Local Kubernetes Cluster with Garden Linux and Lima

Garden Linux makes it easy to run a local Kubernetes cluster using [Lima](https://github.com/lima-vm/lima) as the VM manager. With minimal setup, you can use Garden Linux as the OS for your Kubernetes node, leveraging Lima's templates and automatic port forwarding for seamless access from your host machine.

## Quick Start

1. **Start the VM with Kubernetes:**
```bash
limactl start features/lima/samples/gardenlinux-k8s.yaml
```

2. **Access Kubernetes tools inside the VM:**
```bash
limactl shell gardenlinux-k8s kubectl
```

3. **Access the cluster from your host:**
Export the kubeconfig file (Lima automatically forwards the necessary ports):
```bash
export KUBECONFIG=$(limactl list gardenlinux-k8s --format 'unix://{{.Dir}}/copied-from-guest/kubeconfig.yaml')
kubectl get nodes -o wide
```

Example output:
```
NAME                   STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                KERNEL-VERSION        CONTAINER-RUNTIME
lima-gardenlinux-k8s   Ready    control-plane   75s   v1.35.1   10.x.y.z       <none>        Garden Linux 2150.0.0   6.18.12-cloud-arm64   containerd://2.2.1
```

## Multi-Node Kubernetes Cluster with Lima and Garden Linux

This can also be used for a multi-node cluster using the [user-v2 network](https://lima-vm.io/docs/config/network/user-v2/) in lima.
You'll set up a control-plane node and add a worker node.

### 1. Start the Control-Plane Node

Start your first Kubernetes VM (control-plane):

```bash
limactl start --name k8s-0 --network lima:user-v2 features/lima/samples/gardenlinux-k8s.yaml
```

Follow the prompts to proceed. Lima will download the required images and set up the VM. When setup completes, you'll see a message like:

```
INFO[0091] READY. Run `limactl shell k8s-0` to open the shell.
INFO[0091] Message from the instance "k8s-0":

To run `kubectl` on the host (assumes kubectl is installed), run the following commands:
------
export KUBECONFIG="/Users/user/.lima/k8s-0/copied-from-guest/kubeconfig.yaml"
kubectl ...
------
```

### 2. Get the Join Command

Generate the join command for worker nodes:

```bash
JOIN_COMMAND=$(limactl shell k8s-0 sudo kubeadm token create --print-join-command)
```

### 3. Start the Worker Node

Start a second VM as a worker node:

```bash
limactl start --name k8s-1 --network lima:user-v2 features/lima/samples/gardenlinux-k8s.yaml --set '.param.isWorkerNode="true"'
```

Wait for the VM to be ready.

### 4. Join the Worker Node to the Cluster

Run the join command inside the worker node:

```bash
limactl shell k8s-1 bash -c "sudo $JOIN_COMMAND"
```

You should see output confirming the node has joined the cluster.

### 5. Verify the Cluster

Set your kubeconfig to the control-plane node:

```bash
export KUBECONFIG="/Users/user/.lima/k8s-0/copied-from-guest/kubeconfig.yaml"
```

Check the nodes:

```bash
kubectl get nodes -o wide
```

Example output:

```
NAME         STATUS   ROLES           AGE    VERSION   INTERNAL-IP      EXTERNAL-IP   OS-IMAGE                KERNEL-VERSION        CONTAINER-RUNTIME
lima-k8s-0   Ready    control-plane   104s   v1.35.1   10.x.y.10        <none>        Garden Linux 2150.0.0   6.18.12-cloud-arm64   containerd://2.2.1
lima-k8s-1   Ready    <none>          17s    v1.35.1   10.x.y.11        <none>        Garden Linux 2150.0.0   6.18.12-cloud-arm64   containerd://2.2.1
```

Your multi-node Kubernetes cluster is now running locally!

## Why Use Lima with Garden Linux for Kubernetes?

- **No external dependencies:** Run Kubernetes locally without needing a cloud account - ideal for learning and experimentation.
- **Flexible setup:** Easily customize components like the CNI to suit your needs.
- **Repeatable and automated:** Quickly spin up consistent environments for testing or development.
- **Garden Linux advantages:** Enjoy custom-built Garden Linux packages and an up-to-date LTS kernel for improved performance and security.

## References

- Based on examples by Akihiro Suda and the Lima contributors ([Apache-2.0 license](https://github.com/lima-vm/lima/blob/master/templates/k8s.yaml)).

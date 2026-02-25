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

## Why Use Lima with Garden Linux for Kubernetes?

- **No external dependencies:** Run Kubernetes locally without needing a cloud account - ideal for learning and experimentation.
- **Flexible setup:** Easily customize components like the CNI to suit your needs.
- **Repeatable and automated:** Quickly spin up consistent environments for testing or development.
- **Garden Linux advantages:** Enjoy custom-built Garden Linux packages and an up-to-date LTS kernel for improved performance and security.

## References

- Based on examples by Akihiro Suda and the Lima contributors ([Apache-2.0 license](https://github.com/lima-vm/lima/blob/master/templates/k8s.yaml)).

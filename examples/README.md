# examples

Some show cased howto operate workload based on carbon emission.

Precondition: A installed [Prometheus Stack with Entsoe Exporter](https://github.com/eumel8/carbon-footprint) to provide the current carbon footprint of power generation.

## Update resourcequotas per Cron

In [this cronjob](quota/carbon-cronjob.yaml) a Prometheus API will ask for current carbon state of power generation.
On this decision `resourcequotas` for the target namespace will adjusted.

Works technically but has no effects on running workload or the workload won't start if the quota is reached

## Modify cgroups/cpu.max in Pod

Resourcequotas are realized by cgroup settings in Kubelet and the underlying [Cgroup Driver](https://kubernetes.io/docs/concepts/architecture/cgroups/), which manifests by the underlying Container Runtime Interface(CRI). Usually, and without HostPath this resources are only read-only in the Pod and can't be modified. [Alibaba Cloud](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/dynamically-modify-the-resource-parameters-of-a-pod) has a cgroup controller running, so the user can do this and act as in the example above

## In-Place update Pod resources

In Kubernetes 1.27 this [Kep](https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/1287-in-place-update-pod-resources/kep.yaml) was realized, which makes the resouces in containers.spec writable.

Requires, like K3S start flag:

```bash
...
        --kube-apiserver-arg feature-gates="InPlacePodVerticalScaling=true" \
        --kube-controller-arg feature-gates="InPlacePodVerticalScaling=true" \
        --kubelet-arg feature-gates="InPlacePodVerticalScaling=true" \
```

Then you can use the carbon-cronjob.yaml and make a patch based on the current carbon emission:

```bash
kubectl -n carbon patch pod pod-demo --patch '{"spec":{"containers":[{"name":"pod-demo", "resources":{"requests":{"cpu":"550m"}}}]}}'
pod/pod-demo patched
```

## Deployment Resources

see [./resources/](resources)

Patch deployment and adjust cpu resources based on eco power generation

## Horizontal Pod Autoscaler (HPA)

see [./hpa/](hpa)

Patch hpa and adjust replicas based on eco power generation

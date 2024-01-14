import qsharp
import azure.quantum

qsharp.init(project_root = './RandomNum')
print(qsharp.eval("Sample.RandomNBits(4)"))

result = qsharp.run("Sample.RandomNBits(4)", shots=10)
for x in result:
    print(x)

namespace QCL {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Convert;

    @EntryPoint()
    operation Run() : Result {
        let result = Predict(2, 1, 0.5, [0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4]);
        return result
    }

    operation Predict(n_qubit: Int, depth: Int, x: Double, theta: Double[]) : Result {
        use q = Qubit[n_qubit];
        ResetAll(q);

        Message($"theta: {theta}");

        for i in 0 .. n_qubit - 1 {
            Ry(ArcSin(x) * 2.0, q[i]);
            Rz(ArcSin(x * x) * 2.0, q[i]);
        }
        mutable idx = 0;
        for _ in 0 .. depth - 1 {
            for i in 0 .. n_qubit - 1 {
                for j in 0 .. n_qubit - 1 {
                    if (i != j){
                        CNOT(q[i], q[j]);
                        Rx(theta[idx], q[i]);
                        set idx += 1;
                        Ry(theta[idx], q[i]);
                        set idx += 1;
                        CNOT(q[i], q[j]);
                        Ry(theta[idx], q[i]);
                        set idx += 1;
                        Rx(theta[idx], q[i]);
                        set idx += 1;
                        Message($"idx: {idx}");
                    }         
                }
            }
        }
        Message($"Last idx: {idx}");
        set idx = 0;

        DumpMachine();
        let result = MResetZ(q[1]);
        ResetAll(q);
        return result;
    }

    // operation RandomNBits(N: Int): Result[] {
    //     mutable results = [];
    //     for i in 0 .. N - 1 {
    //        let r = Random();
    //        set results += [r];
    //     }
    //     return results
    // }
}

namespace QCL {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Convert;

    @EntryPoint()
    operation Run() : Int[] {
        let result = Predict(2, 1, 10, 0.5, [0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4]);
        return result
    }

    operation Predict(n_qubit: Int, depth: Int, shots: Int, x: Double, theta: Double[]) : Int[] {
        mutable countArray = [0, 0];

        use q = Qubit[n_qubit];
        for i in 1 .. shots {
            for i in 0 .. n_qubit - 1 {
                Ry(ArcSin(x) * 2.0, q[i]);
                Rz(ArcSin(x * x) * 2.0, q[i]);
            }
            mutable idx = 0;
            for _ in 0 .. depth - 1 {
                for i in 0 .. n_qubit - 1 {
                    if (i != n_qubit - 1){
                        CNOT(q[i], q[i+1]);
                    }
                    Rx(theta[idx], q[i]);
                    set idx += 1;
                    Ry(theta[idx], q[i]);
                    set idx += 1;
                    if (i != n_qubit - 1){
                        CNOT(q[i], q[i+1]);
                    }
                    Ry(theta[idx], q[i]);
                    set idx += 1;
                    Rx(theta[idx], q[i]);
                    set idx += 1;
                    //Message($"idx: {idx}");
                }
            }
            //Message($"Last idx: {idx}");
            let outcome = M(q[0]) == Zero ? 0 | 1;
            set countArray w/= outcome <- countArray[outcome] + 1;
            ResetAll(q);
        }

        return countArray;
    }
}

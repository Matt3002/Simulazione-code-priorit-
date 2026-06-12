simple ModuloCode {
    parameters:
        double p;
        double q;
        double sigma;
        @display("i=block/queue");

       @signal[q1LenSignal](type="int");
        @signal[q2LenSignal](type="int");
        @signal[q1DelaySignal](type="simtime_t");
        @signal[q2DelaySignal](type="simtime_t");
        @signal[q1ThroughputSignal](type="int");
        @signal[q2ThroughputSignal](type="int");

        @statistic[coda1Len](title="Lunghezza Coda 1"; source="q1LenSignal"; record=vector,mean,last; interpolationmode=sample-hold);
        @statistic[coda2Len](title="Lunghezza Coda 2"; source="q2LenSignal"; record=vector,mean,last; interpolationmode=sample-hold);

        @statistic[coda1Delay](title="Tempo Permanenza 1"; source="q1DelaySignal"; record=vector,mean; interpolationmode=none);
        @statistic[coda2Delay](title="Tempo Permanenza 2"; source="q2DelaySignal"; record=vector,mean; interpolationmode=none);

        @statistic[coda1Thru](title="Throughput 1"; source="q1ThroughputSignal"; record=mean);
        @statistic[coda2Thru](title="Throughput 2"; source="q2ThroughputSignal"; record=mean);
}

// Definizione della rete
network SistemaPriorita {
    submodules:
        sistema: ModuloCode;
}
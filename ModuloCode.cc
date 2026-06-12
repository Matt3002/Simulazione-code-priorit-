#include <omnetpp.h>
#include <queue> // Necessario per usare std::queue

using namespace omnetpp;

class ModuloCode : public cSimpleModule {
  private:
    // Usiamo delle code per tenere traccia dei tempi di arrivo dei singoli pacchetti
    std::queue<simtime_t> queue1;
    std::queue<simtime_t> queue2;

    // Parametri
    double p;
    double q;
    double sigma;

    // Identificatori di segnale completi
    simsignal_t q1LenSignal;
    simsignal_t q2LenSignal;
    simsignal_t q1DelaySignal;       // Per il tempo di permanenza
    simsignal_t q2DelaySignal;
    simsignal_t q1ThroughputSignal;  // Per il throughput
    simsignal_t q2ThroughputSignal;

    cMessage *slotEvent;

  protected:
    virtual void initialize() override {
        p = par("p");
        q = par("q");
        sigma = par("sigma");

        // Registrazione dei segnali
        q1LenSignal = registerSignal("q1LenSignal");
        q2LenSignal = registerSignal("q2LenSignal");
        q1DelaySignal = registerSignal("q1DelaySignal");
        q2DelaySignal = registerSignal("q2DelaySignal");
        q1ThroughputSignal = registerSignal("q1ThroughputSignal");
        q2ThroughputSignal = registerSignal("q2ThroughputSignal");

        slotEvent = new cMessage("slotEvent");
        scheduleAt(0.0, slotEvent); // Inizia a t=0
    }

    virtual void handleMessage(cMessage *msg) override {
        // Variabili per il throughput in questo slot (1 se servito, 0 altrimenti)
        int served1 = 0;
        int served2 = 0;

        // --- 1. LOGICA DI SERVIZIO SUI CLIENTI PREESISTENTI ---
        bool serverAvailable = uniform(0, 1) < sigma; // Disponibilità server

        if (serverAvailable) {
            if (!queue1.empty()) {
                // Estrae utente di Coda 1 e calcola il tempo di permanenza
                simtime_t arrivalTime = queue1.front();
                queue1.pop();
                emit(q1DelaySignal, simTime() - arrivalTime);
                served1 = 1;
            } else if (!queue2.empty()) {
                // Estrae utente di Coda 2 solo se Coda 1 è vuota (Priorità Assoluta)
                simtime_t arrivalTime = queue2.front();
                queue2.pop();
                emit(q2DelaySignal, simTime() - arrivalTime);
                served2 = 1;
            }
        }

        // --- 2. GENERAZIONE NUOVI ARRIVI ---
        int a1 = geometric(p); // Tipo 1: Geometrica
        for(int i = 0; i < a1; i++) {
            queue1.push(simTime()); // Salva il tempo di arrivo per ogni utente generato
        }

        int a2 = poisson(q);   // Tipo 2: Poisson
        for(int i = 0; i < a2; i++) {
            queue2.push(simTime());
        }

        // --- 3. RACCOLTA DATI STATISTICI ---
        emit(q1LenSignal, (int)queue1.size());
        emit(q2LenSignal, (int)queue2.size());
        emit(q1ThroughputSignal, served1);
        emit(q2ThroughputSignal, served2);

        // Pianifica il prossimo slot
        scheduleAt(simTime() + 1.0, slotEvent);
    }
};

Define_Module(ModuloCode);

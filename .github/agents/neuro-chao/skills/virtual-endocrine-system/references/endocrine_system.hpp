#pragma once
/**
 * @file endocrine_system.hpp
 * @brief Top-level facade and background agent for the Virtual Endocrine System
 *
 * EndocrineSystem owns the hormone bus, gland registry, valence memory,
 * affective integration, and moral perception layers. It provides a
 * unified interface for initialization and per-tick updates.
 *
 * EndocrineAgent follows the ImportanceDiffusionAgent pattern with
 * start(), stop(), and run_once() for background operation.
 */

#include <opencog/endocrine/moral.hpp>
#include <opencog/endocrine/connector.hpp>
#include <opencog/endocrine/gland.hpp>
#include <opencog/endocrine/glands/hpa_axis.hpp>
#include <opencog/endocrine/glands/dopaminergic.hpp>
#include <opencog/endocrine/glands/serotonergic.hpp>
#include <opencog/endocrine/glands/noradrenergic.hpp>
#include <opencog/endocrine/glands/oxytocinergic.hpp>
#include <opencog/endocrine/glands/thyroid.hpp>
#include <opencog/endocrine/glands/circadian.hpp>
#include <opencog/endocrine/glands/pancreatic.hpp>
#include <opencog/endocrine/glands/immune.hpp>
#include <opencog/endocrine/glands/endocannabinoid.hpp>

#include <atomic>
#include <memory>

namespace opencog::endo {

// ============================================================================
// EndocrineSystem — Top-level facade
// ============================================================================

class EndocrineSystem {
public:
    explicit EndocrineSystem(AtomSpace& space, HormoneBusConfig bus_config = {})
        : space_(space)
        , bus_(bus_config)
        , glands_(bus_)
        , valence_(space)
        , affect_(valence_, bus_, space)
        , moral_(affect_, valence_, bus_, space)
    {
        // Register all default glands
        glands_.register_defaults();
    }

    // === Subsystem Access ===

    [[nodiscard]] HormoneBus& bus() noexcept { return bus_; }
    [[nodiscard]] const HormoneBus& bus() const noexcept { return bus_; }
    [[nodiscard]] GlandRegistry& glands() noexcept { return glands_; }
    [[nodiscard]] ValenceMemory& valence() noexcept { return valence_; }
    [[nodiscard]] AffectiveIntegration& affect() noexcept { return affect_; }
    [[nodiscard]] MoralPerceptionEngine& moral() noexcept { return moral_; }

    // === Typed Gland Access ===

    template<std::derived_from<VirtualGland> G>
    [[nodiscard]] G* gland() noexcept { return glands_.get_gland<G>(); }

    // === Connectors ===

    void connect_attention(AttentionBank& bank) {
        ecan_adapter_ = std::make_unique<ECANEndocrineAdapter>(bus_, bank);
    }

    void connect_pln(pln::PLNEngine& engine) {
        pln_adapter_ = std::make_unique<PLNEndocrineAdapter>(bus_, engine);
    }

    // === Lifecycle ===

    /**
     * @brief Advance the entire system by one tick
     *
     * Order: glands update → bus tick (decay + mode) → adapters modulate →
     *        valence tick → affect computation
     */
    void tick(float dt = 1.0f) {
        // 1. Update all glands (produce hormones)
        glands_.update_all(dt);

        // 2. Tick the bus (decay, history, mode detection)
        bus_.tick();

        // 3. Apply adapter modulations to connected subsystems
        if (ecan_adapter_) {
            ecan_adapter_->apply_endocrine_modulation(bus_);
        }
        if (pln_adapter_) {
            pln_adapter_->apply_endocrine_modulation(bus_);
        }

        // 4. Advance valence memory time
        valence_.tick();
    }

    /**
     * @brief Signal an endocrine event (high-level trigger)
     */
    void signal_event(EndocrineEvent event, float intensity = 1.0f) {
        intensity = std::clamp(intensity, 0.0f, 1.0f);

        switch (event) {
        case EndocrineEvent::THREAT_DETECTED:
            if (auto* hpa = glands_.get_gland<HPAAxis>())
                hpa->signal_stress(intensity);
            if (auto* ne = glands_.get_gland<NoradrenergicGland>())
                ne->signal_novelty(intensity * 0.5f);
            break;

        case EndocrineEvent::REWARD_RECEIVED:
            if (auto* da = glands_.get_gland<DopaminergicGland>())
                da->signal_reward(intensity);
            break;

        case EndocrineEvent::SOCIAL_BOND_SIGNAL:
            if (auto* oxy = glands_.get_gland<OxytocinergicGland>())
                oxy->signal_social(intensity);
            break;

        case EndocrineEvent::RESOURCE_DEPLETED:
            if (auto* panc = glands_.get_gland<PancreaticGland>())
                panc->signal_resource_demand(intensity);
            break;

        case EndocrineEvent::NOVELTY_ENCOUNTERED:
            if (auto* ne = glands_.get_gland<NoradrenergicGland>())
                ne->signal_novelty(intensity);
            break;

        case EndocrineEvent::GOAL_ACHIEVED:
            if (auto* da = glands_.get_gland<DopaminergicGland>())
                da->signal_reward(intensity * 0.8f);
            break;

        case EndocrineEvent::CONFLICT_DETECTED:
            if (auto* hpa = glands_.get_gland<HPAAxis>())
                hpa->signal_stress(intensity * 0.5f);
            if (auto* ne = glands_.get_gland<NoradrenergicGland>())
                ne->signal_novelty(intensity * 0.3f);
            break;

        case EndocrineEvent::UNCERTAINTY_HIGH:
            if (auto* hpa = glands_.get_gland<HPAAxis>())
                hpa->signal_stress(intensity * 0.3f);
            if (auto* ne = glands_.get_gland<NoradrenergicGland>())
                ne->signal_novelty(intensity * 0.5f);
            break;

        case EndocrineEvent::ERROR_DETECTED:
            if (auto* immune = glands_.get_gland<ImmuneMonitor>())
                immune->signal_error(intensity);
            break;

        case EndocrineEvent::NOISE_EXCESSIVE:
            if (auto* ecb = glands_.get_gland<EndocannabinoidGland>())
                ecb->signal_noise(intensity);
            break;

        case EndocrineEvent::LIGHT_SIGNAL:
            if (auto* circ = glands_.get_gland<CircadianGland>())
                circ->signal_light(intensity);
            break;
        }
    }

    // === Configuration ===

    [[nodiscard]] const HormoneBusConfig& config() const noexcept {
        return bus_.config();
    }

private:
    AtomSpace& space_;
    HormoneBus bus_;
    GlandRegistry glands_;
    ValenceMemory valence_;
    AffectiveIntegration affect_;
    MoralPerceptionEngine moral_;

    std::unique_ptr<ECANEndocrineAdapter> ecan_adapter_;
    std::unique_ptr<PLNEndocrineAdapter> pln_adapter_;
};

// ============================================================================
// EndocrineAgent — Background agent (follows ImportanceDiffusionAgent pattern)
// ============================================================================

class EndocrineAgent {
public:
    explicit EndocrineAgent(EndocrineSystem& system)
        : system_(system)
    {}

    ~EndocrineAgent() { stop(); }

    EndocrineAgent(const EndocrineAgent&) = delete;
    EndocrineAgent& operator=(const EndocrineAgent&) = delete;

    void start() { running_.store(true, std::memory_order_release); }
    void stop() { running_.store(false, std::memory_order_release); }

    [[nodiscard]] bool is_running() const noexcept {
        return running_.load(std::memory_order_relaxed);
    }

    /// Execute one update cycle (call from event loop or thread)
    void run_once() {
        if (running_.load(std::memory_order_acquire)) {
            system_.tick(1.0f);
        }
    }

    void set_interval_ms(unsigned int ms) { interval_ms_ = ms; }
    [[nodiscard]] unsigned int interval_ms() const noexcept { return interval_ms_; }

private:
    EndocrineSystem& system_;
    std::atomic<bool> running_{false};
    unsigned int interval_ms_{100};
};

} // namespace opencog::endo

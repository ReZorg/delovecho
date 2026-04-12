#pragma once
/**
 * @file types.hpp
 * @brief Core type definitions for the Virtual Endocrine System (VES)
 *
 * Compact, cache-friendly types for hormonal signaling, valence tagging,
 * and moral perception. All value types follow the 8-byte alignment pattern
 * established by TruthValue and AttentionValue.
 *
 * Design principles:
 * - ValenceSignature and HormoneLevel are 8 bytes (like TruthValue)
 * - EndocrineState is SIMD-aligned for batch operations
 * - HormoneId count padded to 16 (power-of-2) for AVX2 alignment
 */

#include <opencog/core/types.hpp>

#include <array>
#include <cmath>
#include <functional>
#include <string>
#include <string_view>
#include <vector>

namespace opencog::endo {

// ============================================================================
// SIMD alignment constant (matches core/memory.hpp)
// ============================================================================

#if defined(__AVX2__) || defined(__AVX__)
inline constexpr size_t SIMD_ALIGN = 32;
#else
inline constexpr size_t SIMD_ALIGN = 16;
#endif

// ============================================================================
// Hormone Channel Identifiers
// ============================================================================

/// Virtual hormone channels, padded to 16 for SIMD alignment
enum class HormoneId : uint8_t {
    CRH             = 0,   ///< Corticotropin-releasing hormone (hypothalamus)
    ACTH            = 1,   ///< Adrenocorticotropic hormone (pituitary)
    CORTISOL        = 2,   ///< Stress / resource mobilization
    DOPAMINE_TONIC  = 3,   ///< Baseline motivation / cognitive flexibility
    DOPAMINE_PHASIC = 4,   ///< Reward prediction error signal
    SEROTONIN       = 5,   ///< Mood baseline / patience-impulsivity tradeoff
    NOREPINEPHRINE  = 6,   ///< Arousal / vigilance / attention modulation
    OXYTOCIN        = 7,   ///< Trust / bonding / prosocial orientation
    T3_T4           = 8,   ///< Thyroid: global processing rate governor
    MELATONIN       = 9,   ///< Circadian: maintenance cycle scheduling
    INSULIN         = 10,  ///< Energy storage / conservation mode
    GLUCAGON        = 11,  ///< Energy mobilization / active processing
    IL6             = 12,  ///< Cytokine analog: system health signal
    ANANDAMIDE      = 13,  ///< Endocannabinoid: noise reduction / dampening
    RESERVED_1      = 14,  ///< Extension slot
    RESERVED_2      = 15,  ///< Extension slot

    HORMONE_COUNT   = 16   ///< Total channels (power-of-2 for SIMD)
};

inline constexpr size_t HORMONE_COUNT = static_cast<size_t>(HormoneId::HORMONE_COUNT);

/// Human-readable hormone names
[[nodiscard]] constexpr std::string_view hormone_name(HormoneId id) noexcept {
    constexpr std::string_view names[] = {
        "CRH", "ACTH", "Cortisol", "Dopamine(tonic)", "Dopamine(phasic)",
        "Serotonin", "Norepinephrine", "Oxytocin", "T3/T4", "Melatonin",
        "Insulin", "Glucagon", "IL-6", "Anandamide", "Reserved1", "Reserved2"
    };
    auto idx = static_cast<size_t>(id);
    return idx < HORMONE_COUNT ? names[idx] : "Unknown";
}

// ============================================================================
// Valence Signature — 8 bytes (matches TruthValue pattern)
// ============================================================================

/**
 * @brief Affective valence tag for atoms and episodes
 *
 * Two-dimensional affect model (Russell's circumplex):
 * - valence: negative (-1) to positive (+1)
 * - arousal: calm (0) to activated (1)
 *
 * Stored alongside atoms in parallel SoA to tag experiential memories
 * with their felt-quality for later fuzzy retrieval.
 */
struct alignas(8) ValenceSignature {
    float valence{0.0f};  ///< [-1, +1]: negative to positive affect
    float arousal{0.0f};  ///< [0, 1]: calm to activated

    constexpr ValenceSignature() = default;
    constexpr ValenceSignature(float v, float a) : valence(v), arousal(a) {}

    // Named constructors
    [[nodiscard]] static constexpr ValenceSignature neutral() noexcept {
        return {0.0f, 0.0f};
    }
    [[nodiscard]] static constexpr ValenceSignature positive(float intensity = 0.7f) noexcept {
        return {0.7f, intensity};
    }
    [[nodiscard]] static constexpr ValenceSignature negative(float intensity = 0.7f) noexcept {
        return {-0.7f, intensity};
    }
    [[nodiscard]] static constexpr ValenceSignature threat() noexcept {
        return {-0.9f, 0.95f};
    }
    [[nodiscard]] static constexpr ValenceSignature joy() noexcept {
        return {0.8f, 0.7f};
    }
    [[nodiscard]] static constexpr ValenceSignature calm() noexcept {
        return {0.3f, 0.1f};
    }

    /// Magnitude in valence-arousal space
    [[nodiscard]] float magnitude() const noexcept {
        return std::sqrt(valence * valence + arousal * arousal);
    }

    /// Whether this signal is salient enough to matter
    [[nodiscard]] constexpr bool is_salient(float threshold = 0.3f) const noexcept {
        return (valence * valence + arousal * arousal) >= threshold * threshold;
    }

    /// Blend two valence signatures with a weight [0,1] favoring other
    [[nodiscard]] constexpr ValenceSignature blend(const ValenceSignature& other,
                                                    float weight) const noexcept {
        float w = std::clamp(weight, 0.0f, 1.0f);
        return {valence * (1.0f - w) + other.valence * w,
                arousal * (1.0f - w) + other.arousal * w};
    }

    constexpr auto operator<=>(const ValenceSignature&) const = default;
};

static_assert(sizeof(ValenceSignature) == 8);

// ============================================================================
// Hormone Level — 8 bytes
// ============================================================================

/// Current state of a single hormone channel
struct alignas(8) HormoneLevel {
    float concentration{0.0f};  ///< Current level [0, 1] normalized
    float rate{0.0f};           ///< Current production rate (units/tick)

    constexpr HormoneLevel() = default;
    constexpr HormoneLevel(float c, float r) : concentration(c), rate(r) {}

    constexpr auto operator<=>(const HormoneLevel&) const = default;
};

static_assert(sizeof(HormoneLevel) == 8);

// ============================================================================
// Endocrine State — Full snapshot (64 bytes, SIMD-aligned)
// ============================================================================

/// Snapshot of all hormone concentrations at a point in time
struct alignas(SIMD_ALIGN) EndocrineState {
    std::array<float, HORMONE_COUNT> concentrations{};

    [[nodiscard]] float operator[](HormoneId id) const noexcept {
        return concentrations[static_cast<size_t>(id)];
    }
    float& operator[](HormoneId id) noexcept {
        return concentrations[static_cast<size_t>(id)];
    }

    /// Euclidean distance to another state (for mode classification)
    [[nodiscard]] float distance_to(const EndocrineState& other) const noexcept {
        float sum = 0.0f;
        for (size_t i = 0; i < HORMONE_COUNT; ++i) {
            float d = concentrations[i] - other.concentrations[i];
            sum += d * d;
        }
        return std::sqrt(sum);
    }
};

static_assert(sizeof(EndocrineState) == 64);

// ============================================================================
// Cognitive Mode — Emergent attractor state
// ============================================================================

/**
 * @brief Cognitive mode that emerges from the hormone constellation
 *
 * Not set explicitly — classified from the current EndocrineState by
 * nearest-centroid in 16D hormone space. The modes are attractors
 * in the coupled dynamical system of virtual glands.
 */
enum class CognitiveMode : uint8_t {
    RESTING     = 0,  ///< Low arousal, neutral valence
    EXPLORATORY = 1,  ///< Moderate dopamine, low cortisol
    FOCUSED     = 2,  ///< High norepinephrine, moderate cortisol
    STRESSED    = 3,  ///< High cortisol, high norepinephrine
    SOCIAL      = 4,  ///< High oxytocin, moderate serotonin
    REFLECTIVE  = 5,  ///< High serotonin, low norepinephrine
    VIGILANT    = 6,  ///< High norepinephrine, moderate cortisol
    MAINTENANCE = 7,  ///< High melatonin (consolidation/repair)
    REWARD      = 8,  ///< Phasic dopamine burst
    THREAT      = 9,  ///< Full HPA axis activation
};

[[nodiscard]] constexpr std::string_view mode_name(CognitiveMode mode) noexcept {
    constexpr std::string_view names[] = {
        "Resting", "Exploratory", "Focused", "Stressed", "Social",
        "Reflective", "Vigilant", "Maintenance", "Reward", "Threat"
    };
    auto idx = static_cast<size_t>(mode);
    return idx < 10 ? names[idx] : "Unknown";
}

inline constexpr size_t COGNITIVE_MODE_COUNT = 10;

// ============================================================================
// Moral Perception — Aggregated moral signal
// ============================================================================

/**
 * @brief Result of the moral perception pipeline
 *
 * Combines raw affective signal, morally-tagged episode associations,
 * empathic inference, and novelty detection into an actionable moral
 * perception that precedes deliberative moral reasoning.
 */
struct MoralPerception {
    ValenceSignature raw_signal;      ///< 8 bytes: unprocessed valence
    float moral_salience{0.0f};       ///< [0, 1]: how morally significant
    float empathic_weight{0.0f};      ///< [0, 1]: weight from other-modeling
    float novel_moral_signal{0.0f};   ///< [0, 1]: novelty of this moral situation
    CognitiveMode action_bias{CognitiveMode::RESTING}; ///< Suggested response mode
    uint8_t _pad[3]{};

    /// Whether this perception warrants attention
    [[nodiscard]] constexpr bool is_significant(float threshold = 0.3f) const noexcept {
        return moral_salience >= threshold;
    }

    /// Whether this is a novel moral situation (no strong precedent)
    [[nodiscard]] constexpr bool is_novel(float threshold = 0.6f) const noexcept {
        return novel_moral_signal >= threshold;
    }
};

static_assert(sizeof(MoralPerception) == 24);

// ============================================================================
// Felt Sense — Integrated affective state
// ============================================================================

/// Aggregated felt-sense from valence memory integration
struct FeltSense {
    ValenceSignature aggregate_valence;  ///< 8 bytes: weighted centroid
    float certainty{0.0f};              ///< Evidence mass from matches
    float novelty{0.0f};                ///< Inverse of best match confidence
    CognitiveMode suggested_mode{CognitiveMode::RESTING};
    uint8_t _pad[3]{};

    [[nodiscard]] constexpr float discomfort() const noexcept {
        return std::max(0.0f, -aggregate_valence.valence) * aggregate_valence.arousal;
    }

    [[nodiscard]] constexpr float comfort() const noexcept {
        return std::max(0.0f, aggregate_valence.valence) * (1.0f - aggregate_valence.arousal * 0.5f);
    }
};

static_assert(sizeof(FeltSense) == 24);

// ============================================================================
// Release Pattern
// ============================================================================

enum class ReleasePattern : uint8_t {
    TONIC        = 0,  ///< Continuous baseline release
    PULSATILE    = 1,  ///< Rhythmic bursts
    CIRCADIAN    = 2,  ///< 24-hour cycle
    EVENT_DRIVEN = 3,  ///< Triggered by external signals
};

// ============================================================================
// Hormone Channel Configuration
// ============================================================================

struct HormoneChannelConfig {
    HormoneId id{HormoneId::CRH};
    float half_life{1.0f};           ///< Decay half-life in ticks
    float saturation_ceiling{1.0f};  ///< Max concentration
    float baseline{0.0f};            ///< Homeostatic setpoint
    float min_level{0.0f};           ///< Floor concentration
};

// ============================================================================
// Gland Configuration
// ============================================================================

struct GlandConfig {
    std::string name;
    HormoneId output_channel{HormoneId::CRH};
    ReleasePattern release_pattern{ReleasePattern::TONIC};

    float base_production_rate{0.1f};
    float max_production_rate{1.0f};
    float homeostatic_setpoint{0.3f};

    /// Hormone channels that stimulate production: (channel, sensitivity)
    std::vector<std::pair<HormoneId, float>> stimulators;
    /// Hormone channels that inhibit production: (channel, sensitivity)
    std::vector<std::pair<HormoneId, float>> inhibitors;

    /// Negative feedback: own output inhibits own production
    bool negative_feedback{true};
    float feedback_gain{0.5f};

    /// Positive feedback: own output amplifies production (rare, e.g. oxytocin)
    bool positive_feedback{false};
    float positive_feedback_gain{0.0f};

    /// Allostatic shifting: setpoint drift rate under chronic load
    float allostatic_rate{0.001f};
};

// ============================================================================
// Hormone Bus Configuration
// ============================================================================

struct HormoneBusConfig {
    float tick_interval_ms{100.0f};      ///< Nominal update interval
    float global_decay_multiplier{1.0f}; ///< Speed up/slow down all decay
    bool enable_simd{true};              ///< Use SIMD for batch decay
    size_t history_length{1000};         ///< Ring buffer size for snapshots
};

// ============================================================================
// Endocrine Event — Signals that trigger hormonal cascades
// ============================================================================

enum class EndocrineEvent : uint8_t {
    THREAT_DETECTED     = 0,
    REWARD_RECEIVED     = 1,
    SOCIAL_BOND_SIGNAL  = 2,
    RESOURCE_DEPLETED   = 3,
    NOVELTY_ENCOUNTERED = 4,
    GOAL_ACHIEVED       = 5,
    CONFLICT_DETECTED   = 6,
    UNCERTAINTY_HIGH    = 7,
    ERROR_DETECTED      = 8,
    NOISE_EXCESSIVE     = 9,
    LIGHT_SIGNAL        = 10,
};

} // namespace opencog::endo

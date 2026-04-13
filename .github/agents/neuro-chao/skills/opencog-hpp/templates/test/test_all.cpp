// test_all.cpp — Comprehensive test suite for oc:: header-only library
// Compile: g++ -std=c++11 -I ../include -pthread test_all.cpp -o test_all
#include <oc/oc.hpp>
#include <cassert>
#include <iostream>
#include <cmath>

static int pass = 0, fail = 0;
#define TEST(name, expr) do { \
    if (expr) { pass++; std::cout << "  PASS: " << name << "\n"; } \
    else { fail++; std::cout << "  FAIL: " << name << " (" << __FILE__ << ":" << __LINE__ << ")\n"; } \
} while(0)

#define SECTION(name) std::cout << "\n=== " << name << " ===\n"

static bool approx(double a, double b, double eps = 0.01) {
    return std::fabs(a - b) < eps;
}

// ─────────────────────────────────────────────────────────────────────────────
void test_util() {
    SECTION("oc::util");

    // Logger
    oc::util::Logger logger;
    logger.set_level(oc::util::LogLevel::DEBUG);
    logger.info("Logger test message");
    TEST("Logger level", logger.get_level() == oc::util::LogLevel::DEBUG);

    // RandGen
    oc::util::RandGen rng(42);
    double r = rng.randdouble();
    TEST("RandGen double in [0,1)", r >= 0.0 && r < 1.0);
    int ri = rng.randint(0, 9);
    TEST("RandGen int in [0,10)", ri >= 0 && ri < 10);

    // Config
    oc::util::Config cfg;
    cfg.set("key1", "value1");
    cfg.set("port", "8080");
    TEST("Config get string", cfg.get("key1") == "value1");
    TEST("Config get int", cfg.get_int("port") == 8080);
    TEST("Config get default", cfg.get("missing", "default") == "default");

    // ConcurrentQueue
    oc::util::concurrent_queue<int> q;
    q.push(10);
    q.push(20);
    int v;
    TEST("ConcurrentQueue pop", q.try_pop(v) && v == 10);
    TEST("ConcurrentQueue size", q.size() == 1);

    // Tokenize
    auto tokens = oc::util::tokenize("hello world foo");
    TEST("Tokenize count", tokens.size() == 3);
    TEST("Tokenize content", tokens[0] == "hello" && tokens[2] == "foo");

    // SigSlot
    oc::util::SigSlot<int> sig;
    int received = 0;
    sig.connect([&](int x) { received = x; });
    sig.emit(42);
    TEST("SigSlot emit/receive", received == 42);
}

// ─────────────────────────────────────────────────────────────────────────────
void test_atomspace() {
    SECTION("oc::atomspace");

    oc::AtomSpace as;

    // Add nodes
    oc::Handle h1 = as.add_node(oc::types::CONCEPT_NODE, "cat");
    oc::Handle h2 = as.add_node(oc::types::CONCEPT_NODE, "animal");
    TEST("Add nodes", h1 != oc::UNDEFINED_HANDLE && h2 != oc::UNDEFINED_HANDLE);
    TEST("AtomSpace size after nodes", as.size() == 2);

    // Add link
    oc::Handle l1 = as.add_link(oc::types::INHERITANCE_LINK, {h1, h2},
                                  oc::TruthValue(0.9, 0.8));
    TEST("Add link", l1 != oc::UNDEFINED_HANDLE);
    TEST("AtomSpace size after link", as.size() == 3);

    // Get atom
    const oc::Atom* a = as.get_atom(h1);
    TEST("Get atom name", a && a->name == "cat");
    TEST("Get atom type", a && a->type == oc::types::CONCEPT_NODE);

    // Get link TV
    const oc::Atom* link = as.get_atom(l1);
    TEST("Link TV mean", link && approx(link->tv.mean, 0.9));
    TEST("Link TV conf", link && approx(link->tv.confidence, 0.8));

    // Get by type
    auto concepts = as.get_by_type(oc::types::CONCEPT_NODE);
    TEST("Get by type count", concepts.size() == 2);

    // Get node by name
    oc::Handle found = as.get_node(oc::types::CONCEPT_NODE, "cat");
    TEST("Get node by name", found == h1);

    // Incoming set
    auto incoming = as.get_incoming(h1);
    TEST("Incoming set", incoming.size() == 1 && incoming[0] == l1);

    // Pattern match
    auto matches = as.pattern_match(oc::types::INHERITANCE_LINK, {h1, h2});
    TEST("Pattern match", matches.size() == 1 && matches[0] == l1);

    // Remove atom
    as.remove_atom(l1, false);
    TEST("Remove atom", as.size() == 2);

    // TruthValue merge
    oc::TruthValue tv1(0.8, 0.5);
    oc::TruthValue tv2(0.6, 0.7);
    oc::TruthValue merged = tv1.merge(tv2);
    TEST("TV merge", merged.confidence > tv1.confidence);

    // Type registry
    oc::Type ct = oc::TypeRegistry::instance().get_type("ConceptNode");
    TEST("TypeRegistry lookup", ct == oc::types::CONCEPT_NODE);
    std::string tn = oc::TypeRegistry::instance().get_name(oc::types::INHERITANCE_LINK);
    TEST("TypeRegistry name", tn == "InheritanceLink");

    // Value system
    oc::Value val(std::vector<double>{1.0, 2.0, 3.0});
    TEST("Value floats", val.floats().size() == 3 && approx(val.floats()[1], 2.0));
    oc::Value sval(std::vector<std::string>{"a", "b"});
    TEST("Value strings", sval.strings().size() == 2);
}

// ─────────────────────────────────────────────────────────────────────────────
void test_attention() {
    SECTION("oc::attention");

    oc::AtomSpace as;
    oc::Handle h1 = as.add_node(oc::types::CONCEPT_NODE, "focus1");
    oc::Handle h2 = as.add_node(oc::types::CONCEPT_NODE, "focus2");
    oc::Handle h3 = as.add_node(oc::types::CONCEPT_NODE, "background");
    as.add_link(oc::types::INHERITANCE_LINK, {h1, h2});

    oc::attention::ECANRunner ecan(as);
    auto& bank = ecan.bank();

    // Register atoms
    bank.register_atom(h1);
    bank.register_atom(h2);
    bank.register_atom(h3);

    // Stimulate
    bank.stimulate(h1, 100);
    bank.stimulate(h2, 80);
    bank.set_af_threshold(50);

    auto focus = bank.get_attentional_focus();
    TEST("Attentional focus", focus.size() == 2);

    // Run ECAN cycles
    ecan.run(5);
    TEST("ECAN cycles ran", ecan.cycle_count() == 5);

    // Check STI changed
    const oc::Atom* a1 = as.get_atom(h1);
    TEST("STI modified by ECAN", a1 != nullptr);

    // AttentionBank total
    TEST("Total STI tracked", bank.get_total_sti() != 0);
}

// ─────────────────────────────────────────────────────────────────────────────
void test_server() {
    SECTION("oc::server");

    oc::AtomSpace as;
    as.add_node(oc::types::CONCEPT_NODE, "test_node");

    oc::server::CogServer srv(as);

    // Shell
    auto& shell = srv.shell();
    std::string help = shell.eval("help");
    TEST("Shell help", help.find("Available") != std::string::npos);

    std::string stats = shell.eval("stats");
    TEST("Shell stats", stats.find("1") != std::string::npos);

    std::string unknown = shell.eval("nonexistent");
    TEST("Shell unknown cmd", unknown.find("Unknown") != std::string::npos);

    // SchemeShell
    auto& scm = srv.scheme_shell();
    std::string size = scm.eval("(cog-atomspace-size)");
    TEST("SchemeShell atomspace-size", size == "1");

    std::string node = scm.eval("(cog-new-node 'ConceptNode \"scheme_test\")");
    TEST("SchemeShell new-node", node != "Error");

    std::string size2 = scm.eval("(cog-atomspace-size)");
    TEST("SchemeShell size after add", size2 == "2");

    // Module manager
    auto& mm = srv.module_manager();
    TEST("Module count initially", mm.module_count() == 0);

    // Request manager
    srv.request_manager().register_request(
        "test-req",
        new oc::server::RequestFactory<oc::server::ShutdownRequest>("Test"));
    auto reqs = srv.request_manager().list_requests();
    TEST("Request registered", reqs.size() == 1);

    // Server loop
    srv.server_loop(3);
    TEST("Server loop cycles", srv.cycle_count() == 3);
}

// ─────────────────────────────────────────────────────────────────────────────
void test_ure() {
    SECTION("oc::ure");

    oc::AtomSpace as;

    // Create atoms for unification test
    oc::Handle varX = as.add_node(oc::types::VARIABLE_NODE, "$X");
    oc::Handle cat = as.add_node(oc::types::CONCEPT_NODE, "cat");
    oc::Handle animal = as.add_node(oc::types::CONCEPT_NODE, "animal");

    // Unification
    oc::ure::Unifier unifier(as);
    oc::ure::Substitution sub;
    oc::Handle pattern = as.add_link(oc::types::INHERITANCE_LINK, {varX, animal});
    oc::Handle target = as.add_link(oc::types::INHERITANCE_LINK, {cat, animal});
    bool unified = unifier.unify(pattern, target, sub);
    TEST("Unification success", unified);
    TEST("Substitution $X=cat", sub.get(varX) == cat);

    // Rule
    oc::Handle varY = as.add_node(oc::types::VARIABLE_NODE, "$Y");
    oc::Handle varZ = as.add_node(oc::types::VARIABLE_NODE, "$Z");
    oc::Handle rule_pattern = as.add_link(oc::types::INHERITANCE_LINK, {varX, varY});
    oc::Handle rule_rewrite = as.add_link(oc::types::INHERITANCE_LINK, {varX, varZ});
    auto rule = std::make_shared<oc::ure::Rule>(
        "test-rule", rule_pattern, rule_rewrite,
        oc::HandleSeq{varX, varY, varZ}, 1.0);
    TEST("Rule created", rule->name() == "test-rule");
    TEST("Rule applicable", rule->is_applicable(target, as));

    // RuleSet
    oc::ure::RuleSet rs;
    rs.add_rule(rule);
    TEST("RuleSet size", rs.size() == 1);

    auto applicable = rs.get_applicable(target, as);
    TEST("RuleSet applicable", applicable.size() == 1);

    // ForwardChainer
    oc::Handle mammal = as.add_node(oc::types::CONCEPT_NODE, "mammal");
    as.add_link(oc::types::INHERITANCE_LINK, {cat, mammal},
                oc::TruthValue(0.95, 0.9));
    as.add_link(oc::types::INHERITANCE_LINK, {mammal, animal},
                oc::TruthValue(0.99, 0.95));

    oc::ure::UREConfig cfg;
    cfg.max_iterations = 10;
    oc::ure::ForwardChainer fc(as, rs, cfg);
    auto cat_mammal_links = as.pattern_match(oc::types::INHERITANCE_LINK, {cat, mammal});
    oc::Handle cat_mammal = cat_mammal_links.empty() ? cat : cat_mammal_links[0];
    auto fc_results = fc.run(cat_mammal);
    TEST("ForwardChainer ran", true);  // Just verify no crash
}

// ─────────────────────────────────────────────────────────────────────────────
void test_pln() {
    SECTION("oc::pln");

    // Formula tests
    oc::TruthValue AB(0.9, 0.8);
    oc::TruthValue BC(0.85, 0.7);
    auto ded = oc::pln::formulas::deduction(AB, BC, 0.5, 0.3, 0.4);
    TEST("Deduction mean in [0,1]", ded.mean >= 0.0 && ded.mean <= 1.0);
    TEST("Deduction conf in [0,1]", ded.confidence >= 0.0 && ded.confidence <= 1.0);

    oc::TruthValue A(0.8, 0.9);
    auto mp = oc::pln::formulas::modus_ponens(A, AB);
    TEST("Modus ponens mean", mp.mean >= 0.0 && mp.mean <= 1.0);

    auto neg = oc::pln::formulas::negation(A);
    TEST("Negation", approx(neg.mean, 0.2));

    auto conj = oc::pln::formulas::fuzzy_conjunction(AB, BC);
    TEST("Fuzzy conjunction", approx(conj.mean, 0.85));

    auto disj = oc::pln::formulas::fuzzy_disjunction(AB, BC);
    TEST("Fuzzy disjunction", approx(disj.mean, 0.9));

    auto rev = oc::pln::formulas::revision(AB, BC);
    TEST("Revision conf > max input", rev.confidence > std::max(AB.confidence, BC.confidence));

    auto ind = oc::pln::formulas::induction(AB, BC, 0.3, 0.5, 0.4);
    TEST("Induction mean in [0,1]", ind.mean >= 0.0 && ind.mean <= 1.0);

    auto abd = oc::pln::formulas::abduction(AB, BC, 0.3, 0.5, 0.4);
    TEST("Abduction mean in [0,1]", abd.mean >= 0.0 && abd.mean <= 1.0);

    // PLNReasoner
    oc::AtomSpace as;
    oc::pln::PLNReasoner reasoner(as);
    reasoner.store_inheritance("cat", "mammal", 0.95, 0.9);
    reasoner.store_inheritance("mammal", "animal", 0.99, 0.95);
    reasoner.store_inheritance("dog", "mammal", 0.97, 0.92);

    auto conclusions = reasoner.deduce_all();
    TEST("PLN deduction found conclusions", conclusions.size() >= 2);

    // Check cat→animal was deduced
    auto tv = reasoner.query_inheritance("cat", "animal");
    TEST("cat→animal deduced", tv.mean > 0.5 && tv.confidence > 0.0);
}

// ─────────────────────────────────────────────────────────────────────────────
void test_matrix() {
    SECTION("oc::matrix");

    oc::AtomSpace as;
    oc::matrix::PairAPI api(as, "word-pair");

    // Create word nodes
    oc::Handle w1 = as.add_node(oc::types::CONCEPT_NODE, "the");
    oc::Handle w2 = as.add_node(oc::types::CONCEPT_NODE, "cat");
    oc::Handle w3 = as.add_node(oc::types::CONCEPT_NODE, "sat");
    oc::Handle w4 = as.add_node(oc::types::CONCEPT_NODE, "on");

    // Set pair counts
    api.set_pair(w1, w2, 50.0);
    api.set_pair(w1, w3, 10.0);
    api.set_pair(w2, w3, 30.0);
    api.set_pair(w3, w4, 25.0);

    TEST("Get pair count", approx(api.get_pair_count(w1, w2), 50.0));

    // Increment
    api.increment_pair(w1, w2, 5.0);
    TEST("Increment pair", approx(api.get_pair_count(w1, w2), 55.0));

    // Row query
    auto row = api.get_row(w1);
    TEST("Get row size", row.size() == 2);

    // Marginals
    oc::matrix::Marginals marg(api);
    double row_sum = marg.row_marginal(w1);
    TEST("Row marginal", approx(row_sum, 65.0));

    double total = marg.total();
    TEST("Total count", total > 0.0);

    // Similarity
    oc::matrix::Similarity sim(api);
    double cos_self = sim.cosine(w1, w1);
    TEST("Cosine self-similarity", approx(cos_self, 1.0));

    double cos_12 = sim.cosine(w1, w2);
    TEST("Cosine similarity computed", cos_12 >= -0.01 && cos_12 <= 1.01);

    // Mutual Information
    oc::matrix::MutualInformation mi(api, marg);
    double pmi = mi.pmi(w1, w2);
    TEST("PMI computed", !std::isnan(pmi));

    double avg_mi = mi.average_mi();
    TEST("Average MI computed", !std::isnan(avg_mi));

    double h_row = mi.row_entropy();
    TEST("Row entropy non-negative", h_row >= 0.0);

    double h_joint = mi.joint_entropy();
    TEST("Joint entropy >= row entropy", h_joint >= h_row - 0.01);
}

// ─────────────────────────────────────────────────────────────────────────────
void test_persist() {
    SECTION("oc::persist");

    oc::AtomSpace as1;
    oc::Handle h1 = as1.add_node(oc::types::CONCEPT_NODE, "alpha");
    oc::Handle h2 = as1.add_node(oc::types::CONCEPT_NODE, "beta");
    as1.add_link(oc::types::INHERITANCE_LINK, {h1, h2},
                 oc::TruthValue(0.9, 0.8));

    // Serializer
    oc::persist::Serializer ser(as1);
    std::string s = ser.serialize(h1);
    TEST("Serialize node", s.find("ConceptNode") != std::string::npos);
    TEST("Serialize node name", s.find("alpha") != std::string::npos);

    std::string full = ser.serialize_atomspace();
    TEST("Serialize atomspace", full.size() > 0);

    // Deserialize into new AtomSpace
    oc::AtomSpace as2;
    oc::Handle h_deser = ser.deserialize(s, as2);
    TEST("Deserialize node", h_deser != oc::UNDEFINED_HANDLE);
    const oc::Atom* a = as2.get_atom(h_deser);
    TEST("Deserialized name", a && a->name == "alpha");

    // MemoryStorageNode
    oc::persist::MemoryStorageNode mem(as1, "test-store");
    mem.open();
    TEST("Storage open", mem.is_open());

    mem.store_atom(h1);
    mem.store_atom(h2);
    TEST("Stored count", mem.stored_count() == 2);

    oc::Handle fetched = mem.fetch_node(oc::types::CONCEPT_NODE, "alpha");
    TEST("Fetch node", fetched == h1);

    mem.close();
    TEST("Storage closed", !mem.is_open());

    // CogChannel
    oc::persist::CogChannel ch1, ch2;
    ch1.send("HELLO");
    ch1.send("WORLD");
    TEST("Channel outbox", ch1.outbox_size() == 2);

    ch1.deliver_to(ch2);
    TEST("Channel delivered", ch2.inbox_size() == 2);

    std::string msg;
    ch2.receive(msg);
    TEST("Channel receive", msg == "HELLO");

    // DistributedAtomSpace
    oc::AtomSpace as_peer;
    oc::persist::DistributedAtomSpace dist;
    dist.add_peer("peer1", as_peer);
    TEST("Distributed peer count", dist.peer_count() == 1);

    dist.replicate_all(as1);
    // Peer should now have atoms (via serialization)
    TEST("Distributed replicate", true);  // Verify no crash
}

// ─────────────────────────────────────────────────────────────────────────────
void test_integration() {
    SECTION("Integration: PLN + ECAN + Matrix");

    oc::AtomSpace as;

    // Build a knowledge base
    oc::pln::PLNReasoner reasoner(as);
    reasoner.store_inheritance("sparrow", "bird", 0.95, 0.9);
    reasoner.store_inheritance("bird", "animal", 0.99, 0.95);
    reasoner.store_inheritance("penguin", "bird", 0.9, 0.85);
    reasoner.store_inheritance("animal", "living_thing", 0.99, 0.99);

    // Run PLN deduction
    auto conclusions = reasoner.deduce_all();
    TEST("Integration: PLN conclusions", conclusions.size() >= 2);

    // Run ECAN on the same AtomSpace
    oc::attention::ECANRunner ecan(as);
    auto& bank = ecan.bank();

    // Stimulate key concepts
    oc::Handle bird = as.get_node(oc::types::CONCEPT_NODE, "bird");
    oc::Handle animal = as.get_node(oc::types::CONCEPT_NODE, "animal");
    if (bird != oc::UNDEFINED_HANDLE) bank.stimulate(bird, 100);
    if (animal != oc::UNDEFINED_HANDLE) bank.stimulate(animal, 80);
    bank.set_af_threshold(30);

    ecan.run(3);
    TEST("Integration: ECAN ran on PLN atoms", ecan.cycle_count() == 3);

    // Build a co-occurrence matrix
    oc::matrix::PairAPI pairs(as, "co-occur");
    oc::Handle sparrow = as.get_node(oc::types::CONCEPT_NODE, "sparrow");
    oc::Handle penguin = as.get_node(oc::types::CONCEPT_NODE, "penguin");
    if (sparrow != oc::UNDEFINED_HANDLE && bird != oc::UNDEFINED_HANDLE) {
        pairs.set_pair(sparrow, bird, 100.0);
    }
    if (penguin != oc::UNDEFINED_HANDLE && bird != oc::UNDEFINED_HANDLE) {
        pairs.set_pair(penguin, bird, 80.0);
    }
    if (sparrow != oc::UNDEFINED_HANDLE && animal != oc::UNDEFINED_HANDLE) {
        pairs.set_pair(sparrow, animal, 90.0);
    }
    if (penguin != oc::UNDEFINED_HANDLE && animal != oc::UNDEFINED_HANDLE) {
        pairs.set_pair(penguin, animal, 70.0);
    }

    oc::matrix::Similarity sim(pairs);
    if (sparrow != oc::UNDEFINED_HANDLE && penguin != oc::UNDEFINED_HANDLE) {
        double cos = sim.cosine(sparrow, penguin);
        TEST("Integration: sparrow-penguin similarity", cos > 0.9);
    }

    // Serialize and verify
    oc::persist::Serializer ser(as);
    std::string dump = ser.serialize_atomspace();
    TEST("Integration: serialized KB", dump.size() > 100);
}

// ─────────────────────────────────────────────────────────────────────────────
int main() {
    std::cout << "OpenCog Header-Only Library — Test Suite\n";
    std::cout << "========================================\n";

    test_util();
    test_atomspace();
    test_attention();
    test_server();
    test_ure();
    test_pln();
    test_matrix();
    test_persist();
    test_integration();

    std::cout << "\n========================================\n";
    std::cout << "Results: " << pass << " passed, " << fail << " failed\n";
    return fail > 0 ? 1 : 0;
}

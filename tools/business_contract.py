"""Test traceability for the canonical metamodel, never another business model.

Links declare which executable regression checks cover each rule. They do not
claim line coverage. The runner records which linked tests actually passed.
"""
import unittest
from estimation_calculation import metamodel
from validation_reporting import test_ids
from validate_stacks import ROOT

ALGORITHM_CHECKS = {
 'role_allocation': 'test_estimation_calculation.EstimationCalculationTests.test_four_references_and_adoption_reproduce',
 'retained_rounding': 'test_estimation_calculation.EstimationCalculationTests.test_four_references_and_adoption_reproduce',
 'nonlinear_complements': 'test_estimation_audit.AuditCorrectionsTests.test_reconstructed_counts_and_costs',
 'economic_total': 'test_retained_core.RetainedCoreTests.test_adopted_scope_role_sum_and_cost_identity',
 'eligible_gains': 'test_maintenance_specialisation.MaintenanceSpecialisationTests.test_only_financed_n3_days_are_eligible_and_their_gain_is_respected',
 'annual_work_cost': 'test_maintenance_specialisation.MaintenanceSpecialisationTests.test_specialisation_reprices_existing_days_and_does_not_add_effort',
 'inflation': 'test_composable_costs.ComposableTests.test_buy_schedule_matches_independent_monthly_calculation',
 'period_allocation': 'test_composable_costs.ComposableTests.test_buy_schedule_matches_independent_monthly_calculation',
 'horizon_total': 'test_composable_costs.ComposableTests.test_funding_once_and_all_horizons_reconcile',
 'calculation_binding': 'test_estimation_audit.AuditCorrectionsTests.test_clone_or_reassignment_cannot_reuse_master_data_calculation',
 'evidence_closure': 'test_estimation_audit.AuditCorrectionsTests.test_evidence_hashes_and_dependency_graph_are_enforced',
 'unique_mechanism_funding': 'test_estimation_audit.AuditCorrectionsTests.test_shared_mechanism_cannot_be_funded_twice',
 'decision_consolidation': 'test_estimation_audit.AuditCorrectionsTests.test_comparability_and_consolidation_are_not_probabilities',
 'prepare_size': 'test_estimation_audit.AuditCorrectionsTests.test_reconstructed_counts_and_costs',
 'cosmic_count': 'test_estimation_audit.AuditCorrectionsTests.test_cosmic_structure_and_counts_are_recomputed',
 'comparison_contract': 'test_estimation_audit.AuditCorrectionsTests.test_comparability_and_consolidation_are_not_probabilities',
 'component_attribution': 'test_stock_adoption.StockAdoptionTests.test_native_sizes_and_functional_count_reconstructed',
 'funded_module_preparation': 'test_ownership_adoption.OwnershipAdoptionTests.test_native_new_sizes_and_COSMIC_reconstructed',
 'coherent_component_preparation': 'test_complete_core_adoption.CompleteCoreAdoptionTests.test_global_roles_coverage_and_valuation_reconcile_without_common_surcharge',
 'product_purpose_partition': 'test_core_product_scope.ProductScopeTests.test_both_purposes_conserve_each_role_and_cost',
 'complete_product_proposal': 'test_core_product_scope.ProductScopeTests.test_reference_and_replacement_are_separate',
 'professional_component_preparation': 'test_professional_adoption.ProfessionalAdoptionTests.test_three_calculations_replay_from_exported_documents_without_io',
}


def coverage_report(model=None, available=None):
    model = metamodel() if model is None else model
    if available is None:
        available = set(test_ids(unittest.TestLoader().discover(str(ROOT / 'tools'))))
    from test_business_contract import ARITHMETIC_CASES
    declared = dict(ALGORITHM_CHECKS)
    declared.update({key: 'test_business_contract.ArithmeticContractTests.test_' + key for key in ARITHMETIC_CASES})
    rules = {r['id'] for r in model['rules']}
    if rules != declared.keys():
        raise ValueError('Rule coverage drift: missing=' + str(sorted(rules - declared.keys())) + ', stale=' + str(sorted(declared.keys() - rules)))
    missing = set(declared.values()) - set(available)
    if missing:
        raise ValueError('Missing executable contract tests: ' + str(sorted(missing)))
    owners = {rule: item['path'] for item in model['implementations'] for rule in item['rules']}
    return {'rules': [{'id': rule, 'implementation': owners[rule], 'test': declared[rule]} for rule in sorted(rules)],
            'test_ids': sorted(set(declared.values())), 'canonical': 'source/fondamentaux.yaml#estimation_model',
            'meaning': 'Declared rule-to-regression traceability, not line or branch coverage'}

"""Utilities for checking allow/deny rules."""

from typing import Any, Dict, List, Optional, Union


RuleType = Dict[str, Any]
RulesType = List[RuleType]


class RuleChecker:
    """Class for checking allow/deny rules."""

    @staticmethod
    def check_rules(context: Dict[str, Any], allow_rules: Optional[RulesType], 
                   deny_rules: Optional[RulesType]) -> bool:
        """Check if the context is allowed based on allow/deny rules.
        
        Args:
            context: The context to check against the rules.
            allow_rules: Rules that allow access if matched.
            deny_rules: Rules that deny access if matched (takes precedence).
            
        Returns:
            bool: True if access is allowed, False otherwise.
        """
        # If there are no rules, default to deny
        if not allow_rules and not deny_rules:
            return False
            
        # Check deny rules first (they take precedence)
        if deny_rules and RuleChecker._matches_any_rule(context, deny_rules):
            return False
            
        # If there are no allow rules, and no deny rules matched, allow access
        if not allow_rules:
            return True
            
        # Check if any allow rule matches
        return RuleChecker._matches_any_rule(context, allow_rules)
    
    @staticmethod
    def _matches_any_rule(context: Dict[str, Any], rules: RulesType) -> bool:
        """Check if the context matches any of the rules.
        
        Args:
            context: The context to check against the rules.
            rules: The rules to check.
            
        Returns:
            bool: True if any rule matches, False otherwise.
        """
        for rule in rules:
            if RuleChecker._matches_rule(context, rule):
                return True
        return False
    
    @staticmethod
    def _matches_rule(context: Dict[str, Any], rule: RuleType) -> bool:
        """Check if the context matches a specific rule.
        
        Args:
            context: The context to check against the rule.
            rule: The rule to check.
            
        Returns:
            bool: True if the rule matches, False otherwise.
        """
        field = rule.get("field")
        values = rule.get("values", [])
        
        if not field or not values:
            return False
            
        # Check if the field exists in the context
        if field not in context:
            return False
            
        # Check if the context value matches any of the rule values
        context_value = context[field]
        
        # Handle different types of context values
        if isinstance(context_value, list):
            # Check if any value in the context list matches any value in the rule values
            return any(value in values for value in context_value)
        else:
            # Check if the context value is in the rule values
            return context_value in values
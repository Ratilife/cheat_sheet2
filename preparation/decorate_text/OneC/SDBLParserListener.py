# Generated from SDBLParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .SDBLParser import SDBLParser
else:
    from SDBLParser import SDBLParser

# This class defines a complete listener for a parse tree produced by SDBLParser.
class SDBLParserListener(ParseTreeListener):

    # Enter a parse tree produced by SDBLParser#queryPackage.
    def enterQueryPackage(self, ctx:SDBLParser.QueryPackageContext):
        pass

    # Exit a parse tree produced by SDBLParser#queryPackage.
    def exitQueryPackage(self, ctx:SDBLParser.QueryPackageContext):
        pass


    # Enter a parse tree produced by SDBLParser#queries.
    def enterQueries(self, ctx:SDBLParser.QueriesContext):
        pass

    # Exit a parse tree produced by SDBLParser#queries.
    def exitQueries(self, ctx:SDBLParser.QueriesContext):
        pass


    # Enter a parse tree produced by SDBLParser#dropTableQuery.
    def enterDropTableQuery(self, ctx:SDBLParser.DropTableQueryContext):
        pass

    # Exit a parse tree produced by SDBLParser#dropTableQuery.
    def exitDropTableQuery(self, ctx:SDBLParser.DropTableQueryContext):
        pass


    # Enter a parse tree produced by SDBLParser#selectQuery.
    def enterSelectQuery(self, ctx:SDBLParser.SelectQueryContext):
        pass

    # Exit a parse tree produced by SDBLParser#selectQuery.
    def exitSelectQuery(self, ctx:SDBLParser.SelectQueryContext):
        pass


    # Enter a parse tree produced by SDBLParser#subquery.
    def enterSubquery(self, ctx:SDBLParser.SubqueryContext):
        pass

    # Exit a parse tree produced by SDBLParser#subquery.
    def exitSubquery(self, ctx:SDBLParser.SubqueryContext):
        pass


    # Enter a parse tree produced by SDBLParser#union.
    def enterUnion(self, ctx:SDBLParser.UnionContext):
        pass

    # Exit a parse tree produced by SDBLParser#union.
    def exitUnion(self, ctx:SDBLParser.UnionContext):
        pass


    # Enter a parse tree produced by SDBLParser#query.
    def enterQuery(self, ctx:SDBLParser.QueryContext):
        pass

    # Exit a parse tree produced by SDBLParser#query.
    def exitQuery(self, ctx:SDBLParser.QueryContext):
        pass


    # Enter a parse tree produced by SDBLParser#limitations.
    def enterLimitations(self, ctx:SDBLParser.LimitationsContext):
        pass

    # Exit a parse tree produced by SDBLParser#limitations.
    def exitLimitations(self, ctx:SDBLParser.LimitationsContext):
        pass


    # Enter a parse tree produced by SDBLParser#top.
    def enterTop(self, ctx:SDBLParser.TopContext):
        pass

    # Exit a parse tree produced by SDBLParser#top.
    def exitTop(self, ctx:SDBLParser.TopContext):
        pass


    # Enter a parse tree produced by SDBLParser#selectedFields.
    def enterSelectedFields(self, ctx:SDBLParser.SelectedFieldsContext):
        pass

    # Exit a parse tree produced by SDBLParser#selectedFields.
    def exitSelectedFields(self, ctx:SDBLParser.SelectedFieldsContext):
        pass


    # Enter a parse tree produced by SDBLParser#selectedField.
    def enterSelectedField(self, ctx:SDBLParser.SelectedFieldContext):
        pass

    # Exit a parse tree produced by SDBLParser#selectedField.
    def exitSelectedField(self, ctx:SDBLParser.SelectedFieldContext):
        pass


    # Enter a parse tree produced by SDBLParser#asteriskField.
    def enterAsteriskField(self, ctx:SDBLParser.AsteriskFieldContext):
        pass

    # Exit a parse tree produced by SDBLParser#asteriskField.
    def exitAsteriskField(self, ctx:SDBLParser.AsteriskFieldContext):
        pass


    # Enter a parse tree produced by SDBLParser#expressionField.
    def enterExpressionField(self, ctx:SDBLParser.ExpressionFieldContext):
        pass

    # Exit a parse tree produced by SDBLParser#expressionField.
    def exitExpressionField(self, ctx:SDBLParser.ExpressionFieldContext):
        pass


    # Enter a parse tree produced by SDBLParser#columnField.
    def enterColumnField(self, ctx:SDBLParser.ColumnFieldContext):
        pass

    # Exit a parse tree produced by SDBLParser#columnField.
    def exitColumnField(self, ctx:SDBLParser.ColumnFieldContext):
        pass


    # Enter a parse tree produced by SDBLParser#emptyTableField.
    def enterEmptyTableField(self, ctx:SDBLParser.EmptyTableFieldContext):
        pass

    # Exit a parse tree produced by SDBLParser#emptyTableField.
    def exitEmptyTableField(self, ctx:SDBLParser.EmptyTableFieldContext):
        pass


    # Enter a parse tree produced by SDBLParser#emptyTableColumns.
    def enterEmptyTableColumns(self, ctx:SDBLParser.EmptyTableColumnsContext):
        pass

    # Exit a parse tree produced by SDBLParser#emptyTableColumns.
    def exitEmptyTableColumns(self, ctx:SDBLParser.EmptyTableColumnsContext):
        pass


    # Enter a parse tree produced by SDBLParser#inlineTableField.
    def enterInlineTableField(self, ctx:SDBLParser.InlineTableFieldContext):
        pass

    # Exit a parse tree produced by SDBLParser#inlineTableField.
    def exitInlineTableField(self, ctx:SDBLParser.InlineTableFieldContext):
        pass


    # Enter a parse tree produced by SDBLParser#recordAutoNumberFunction.
    def enterRecordAutoNumberFunction(self, ctx:SDBLParser.RecordAutoNumberFunctionContext):
        pass

    # Exit a parse tree produced by SDBLParser#recordAutoNumberFunction.
    def exitRecordAutoNumberFunction(self, ctx:SDBLParser.RecordAutoNumberFunctionContext):
        pass


    # Enter a parse tree produced by SDBLParser#groupByItem.
    def enterGroupByItem(self, ctx:SDBLParser.GroupByItemContext):
        pass

    # Exit a parse tree produced by SDBLParser#groupByItem.
    def exitGroupByItem(self, ctx:SDBLParser.GroupByItemContext):
        pass


    # Enter a parse tree produced by SDBLParser#indexingItem.
    def enterIndexingItem(self, ctx:SDBLParser.IndexingItemContext):
        pass

    # Exit a parse tree produced by SDBLParser#indexingItem.
    def exitIndexingItem(self, ctx:SDBLParser.IndexingItemContext):
        pass


    # Enter a parse tree produced by SDBLParser#orderBy.
    def enterOrderBy(self, ctx:SDBLParser.OrderByContext):
        pass

    # Exit a parse tree produced by SDBLParser#orderBy.
    def exitOrderBy(self, ctx:SDBLParser.OrderByContext):
        pass


    # Enter a parse tree produced by SDBLParser#ordersByExpession.
    def enterOrdersByExpession(self, ctx:SDBLParser.OrdersByExpessionContext):
        pass

    # Exit a parse tree produced by SDBLParser#ordersByExpession.
    def exitOrdersByExpession(self, ctx:SDBLParser.OrdersByExpessionContext):
        pass


    # Enter a parse tree produced by SDBLParser#totalBy.
    def enterTotalBy(self, ctx:SDBLParser.TotalByContext):
        pass

    # Exit a parse tree produced by SDBLParser#totalBy.
    def exitTotalBy(self, ctx:SDBLParser.TotalByContext):
        pass


    # Enter a parse tree produced by SDBLParser#totalsGroup.
    def enterTotalsGroup(self, ctx:SDBLParser.TotalsGroupContext):
        pass

    # Exit a parse tree produced by SDBLParser#totalsGroup.
    def exitTotalsGroup(self, ctx:SDBLParser.TotalsGroupContext):
        pass


    # Enter a parse tree produced by SDBLParser#periodic.
    def enterPeriodic(self, ctx:SDBLParser.PeriodicContext):
        pass

    # Exit a parse tree produced by SDBLParser#periodic.
    def exitPeriodic(self, ctx:SDBLParser.PeriodicContext):
        pass


    # Enter a parse tree produced by SDBLParser#column.
    def enterColumn(self, ctx:SDBLParser.ColumnContext):
        pass

    # Exit a parse tree produced by SDBLParser#column.
    def exitColumn(self, ctx:SDBLParser.ColumnContext):
        pass


    # Enter a parse tree produced by SDBLParser#expression.
    def enterExpression(self, ctx:SDBLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by SDBLParser#expression.
    def exitExpression(self, ctx:SDBLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by SDBLParser#primitiveExpression.
    def enterPrimitiveExpression(self, ctx:SDBLParser.PrimitiveExpressionContext):
        pass

    # Exit a parse tree produced by SDBLParser#primitiveExpression.
    def exitPrimitiveExpression(self, ctx:SDBLParser.PrimitiveExpressionContext):
        pass


    # Enter a parse tree produced by SDBLParser#caseExpression.
    def enterCaseExpression(self, ctx:SDBLParser.CaseExpressionContext):
        pass

    # Exit a parse tree produced by SDBLParser#caseExpression.
    def exitCaseExpression(self, ctx:SDBLParser.CaseExpressionContext):
        pass


    # Enter a parse tree produced by SDBLParser#caseBranch.
    def enterCaseBranch(self, ctx:SDBLParser.CaseBranchContext):
        pass

    # Exit a parse tree produced by SDBLParser#caseBranch.
    def exitCaseBranch(self, ctx:SDBLParser.CaseBranchContext):
        pass


    # Enter a parse tree produced by SDBLParser#bracketExpression.
    def enterBracketExpression(self, ctx:SDBLParser.BracketExpressionContext):
        pass

    # Exit a parse tree produced by SDBLParser#bracketExpression.
    def exitBracketExpression(self, ctx:SDBLParser.BracketExpressionContext):
        pass


    # Enter a parse tree produced by SDBLParser#unaryExpression.
    def enterUnaryExpression(self, ctx:SDBLParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by SDBLParser#unaryExpression.
    def exitUnaryExpression(self, ctx:SDBLParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by SDBLParser#functionCall.
    def enterFunctionCall(self, ctx:SDBLParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by SDBLParser#functionCall.
    def exitFunctionCall(self, ctx:SDBLParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by SDBLParser#builtInFunctions.
    def enterBuiltInFunctions(self, ctx:SDBLParser.BuiltInFunctionsContext):
        pass

    # Exit a parse tree produced by SDBLParser#builtInFunctions.
    def exitBuiltInFunctions(self, ctx:SDBLParser.BuiltInFunctionsContext):
        pass


    # Enter a parse tree produced by SDBLParser#aggregateFunctions.
    def enterAggregateFunctions(self, ctx:SDBLParser.AggregateFunctionsContext):
        pass

    # Exit a parse tree produced by SDBLParser#aggregateFunctions.
    def exitAggregateFunctions(self, ctx:SDBLParser.AggregateFunctionsContext):
        pass


    # Enter a parse tree produced by SDBLParser#valueFunction.
    def enterValueFunction(self, ctx:SDBLParser.ValueFunctionContext):
        pass

    # Exit a parse tree produced by SDBLParser#valueFunction.
    def exitValueFunction(self, ctx:SDBLParser.ValueFunctionContext):
        pass


    # Enter a parse tree produced by SDBLParser#castFunction.
    def enterCastFunction(self, ctx:SDBLParser.CastFunctionContext):
        pass

    # Exit a parse tree produced by SDBLParser#castFunction.
    def exitCastFunction(self, ctx:SDBLParser.CastFunctionContext):
        pass


    # Enter a parse tree produced by SDBLParser#logicalExpression.
    def enterLogicalExpression(self, ctx:SDBLParser.LogicalExpressionContext):
        pass

    # Exit a parse tree produced by SDBLParser#logicalExpression.
    def exitLogicalExpression(self, ctx:SDBLParser.LogicalExpressionContext):
        pass


    # Enter a parse tree produced by SDBLParser#predicate.
    def enterPredicate(self, ctx:SDBLParser.PredicateContext):
        pass

    # Exit a parse tree produced by SDBLParser#predicate.
    def exitPredicate(self, ctx:SDBLParser.PredicateContext):
        pass


    # Enter a parse tree produced by SDBLParser#likePredicate.
    def enterLikePredicate(self, ctx:SDBLParser.LikePredicateContext):
        pass

    # Exit a parse tree produced by SDBLParser#likePredicate.
    def exitLikePredicate(self, ctx:SDBLParser.LikePredicateContext):
        pass


    # Enter a parse tree produced by SDBLParser#isNullPredicate.
    def enterIsNullPredicate(self, ctx:SDBLParser.IsNullPredicateContext):
        pass

    # Exit a parse tree produced by SDBLParser#isNullPredicate.
    def exitIsNullPredicate(self, ctx:SDBLParser.IsNullPredicateContext):
        pass


    # Enter a parse tree produced by SDBLParser#comparePredicate.
    def enterComparePredicate(self, ctx:SDBLParser.ComparePredicateContext):
        pass

    # Exit a parse tree produced by SDBLParser#comparePredicate.
    def exitComparePredicate(self, ctx:SDBLParser.ComparePredicateContext):
        pass


    # Enter a parse tree produced by SDBLParser#betweenPredicate.
    def enterBetweenPredicate(self, ctx:SDBLParser.BetweenPredicateContext):
        pass

    # Exit a parse tree produced by SDBLParser#betweenPredicate.
    def exitBetweenPredicate(self, ctx:SDBLParser.BetweenPredicateContext):
        pass


    # Enter a parse tree produced by SDBLParser#inPredicate.
    def enterInPredicate(self, ctx:SDBLParser.InPredicateContext):
        pass

    # Exit a parse tree produced by SDBLParser#inPredicate.
    def exitInPredicate(self, ctx:SDBLParser.InPredicateContext):
        pass


    # Enter a parse tree produced by SDBLParser#refsPredicate.
    def enterRefsPredicate(self, ctx:SDBLParser.RefsPredicateContext):
        pass

    # Exit a parse tree produced by SDBLParser#refsPredicate.
    def exitRefsPredicate(self, ctx:SDBLParser.RefsPredicateContext):
        pass


    # Enter a parse tree produced by SDBLParser#expressionList.
    def enterExpressionList(self, ctx:SDBLParser.ExpressionListContext):
        pass

    # Exit a parse tree produced by SDBLParser#expressionList.
    def exitExpressionList(self, ctx:SDBLParser.ExpressionListContext):
        pass


    # Enter a parse tree produced by SDBLParser#dataSources.
    def enterDataSources(self, ctx:SDBLParser.DataSourcesContext):
        pass

    # Exit a parse tree produced by SDBLParser#dataSources.
    def exitDataSources(self, ctx:SDBLParser.DataSourcesContext):
        pass


    # Enter a parse tree produced by SDBLParser#dataSource.
    def enterDataSource(self, ctx:SDBLParser.DataSourceContext):
        pass

    # Exit a parse tree produced by SDBLParser#dataSource.
    def exitDataSource(self, ctx:SDBLParser.DataSourceContext):
        pass


    # Enter a parse tree produced by SDBLParser#table.
    def enterTable(self, ctx:SDBLParser.TableContext):
        pass

    # Exit a parse tree produced by SDBLParser#table.
    def exitTable(self, ctx:SDBLParser.TableContext):
        pass


    # Enter a parse tree produced by SDBLParser#virtualTable.
    def enterVirtualTable(self, ctx:SDBLParser.VirtualTableContext):
        pass

    # Exit a parse tree produced by SDBLParser#virtualTable.
    def exitVirtualTable(self, ctx:SDBLParser.VirtualTableContext):
        pass


    # Enter a parse tree produced by SDBLParser#virtualTableParameter.
    def enterVirtualTableParameter(self, ctx:SDBLParser.VirtualTableParameterContext):
        pass

    # Exit a parse tree produced by SDBLParser#virtualTableParameter.
    def exitVirtualTableParameter(self, ctx:SDBLParser.VirtualTableParameterContext):
        pass


    # Enter a parse tree produced by SDBLParser#parameterTable.
    def enterParameterTable(self, ctx:SDBLParser.ParameterTableContext):
        pass

    # Exit a parse tree produced by SDBLParser#parameterTable.
    def exitParameterTable(self, ctx:SDBLParser.ParameterTableContext):
        pass


    # Enter a parse tree produced by SDBLParser#externalDataSourceTable.
    def enterExternalDataSourceTable(self, ctx:SDBLParser.ExternalDataSourceTableContext):
        pass

    # Exit a parse tree produced by SDBLParser#externalDataSourceTable.
    def exitExternalDataSourceTable(self, ctx:SDBLParser.ExternalDataSourceTableContext):
        pass


    # Enter a parse tree produced by SDBLParser#joinPart.
    def enterJoinPart(self, ctx:SDBLParser.JoinPartContext):
        pass

    # Exit a parse tree produced by SDBLParser#joinPart.
    def exitJoinPart(self, ctx:SDBLParser.JoinPartContext):
        pass


    # Enter a parse tree produced by SDBLParser#alias.
    def enterAlias(self, ctx:SDBLParser.AliasContext):
        pass

    # Exit a parse tree produced by SDBLParser#alias.
    def exitAlias(self, ctx:SDBLParser.AliasContext):
        pass


    # Enter a parse tree produced by SDBLParser#datePart.
    def enterDatePart(self, ctx:SDBLParser.DatePartContext):
        pass

    # Exit a parse tree produced by SDBLParser#datePart.
    def exitDatePart(self, ctx:SDBLParser.DatePartContext):
        pass


    # Enter a parse tree produced by SDBLParser#multiString.
    def enterMultiString(self, ctx:SDBLParser.MultiStringContext):
        pass

    # Exit a parse tree produced by SDBLParser#multiString.
    def exitMultiString(self, ctx:SDBLParser.MultiStringContext):
        pass


    # Enter a parse tree produced by SDBLParser#sign.
    def enterSign(self, ctx:SDBLParser.SignContext):
        pass

    # Exit a parse tree produced by SDBLParser#sign.
    def exitSign(self, ctx:SDBLParser.SignContext):
        pass


    # Enter a parse tree produced by SDBLParser#identifier.
    def enterIdentifier(self, ctx:SDBLParser.IdentifierContext):
        pass

    # Exit a parse tree produced by SDBLParser#identifier.
    def exitIdentifier(self, ctx:SDBLParser.IdentifierContext):
        pass


    # Enter a parse tree produced by SDBLParser#temporaryTableIdentifier.
    def enterTemporaryTableIdentifier(self, ctx:SDBLParser.TemporaryTableIdentifierContext):
        pass

    # Exit a parse tree produced by SDBLParser#temporaryTableIdentifier.
    def exitTemporaryTableIdentifier(self, ctx:SDBLParser.TemporaryTableIdentifierContext):
        pass


    # Enter a parse tree produced by SDBLParser#parameter.
    def enterParameter(self, ctx:SDBLParser.ParameterContext):
        pass

    # Exit a parse tree produced by SDBLParser#parameter.
    def exitParameter(self, ctx:SDBLParser.ParameterContext):
        pass


    # Enter a parse tree produced by SDBLParser#mdo.
    def enterMdo(self, ctx:SDBLParser.MdoContext):
        pass

    # Exit a parse tree produced by SDBLParser#mdo.
    def exitMdo(self, ctx:SDBLParser.MdoContext):
        pass



del SDBLParser
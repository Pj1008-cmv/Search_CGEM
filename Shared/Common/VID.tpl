Version 1.0;
ProgramStyle = Modular;

TestPlan VID;
Test ReadVisualIdFromCatts GetVisualId
{
    Ult = Ults.Cpu;
    Timeout = "00:00:20";
}

Flow VID
{
    #FlowItem FirstTest GetVisualId
    #{
    #    Result -1
    #    {
    #        Property PassFail = "Fail";
    #        Return 0;
    #    }
    #    Result 0
    #    {
    #        Property PassFail = "Fail";
    #        Return 0;
    #    }
    #    Result 1
    #    {
    #        Property PassFail = "Pass";
    #        # Assign VisualId to UserVar for later use/logging
    #        Set SCVars.VisualId = $Result.VisualId;
    #        Return 1;
    #    }
    #}
}
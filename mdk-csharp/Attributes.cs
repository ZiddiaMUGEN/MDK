namespace MDK
{
    /// <summary>
    /// Used to specify a function will be included for compilation to CNS as a state definition.
    /// </summary>
    public class StateAttribute : Attribute
    {
        public StateAttribute(int? StateNo = null)
        {

        }
    }

    /// <summary>
    /// Used to specify a function will be included as a MTL template definition.
    /// </summary>
    public class TemplateAttribute : Attribute
    {
    }

    /// <summary>
    /// Used to specify a function will be included as a MTL trigger definition.
    /// </summary>
    public class TriggerAttribute : Attribute
    {
    }

    /// <summary>
    /// Used to specify a function will be included as a MTL type definition.
    /// </summary>
    public class TypeAttribute : Attribute
    {
    }
}

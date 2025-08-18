using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.Text;
using System.Text;

namespace MDK;

[Generator]
public class CNSGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        // this needs to search for the MDK.State, MDK.Template, MDK.Trigger, MDK.Type attributes
        // and convert them into include/state files.
        context.RegisterPostInitializationOutput(ctx => ctx.AddSource(
            "EnumExtensionsAttribute.g.cs",
            SourceText.From("EFGH", Encoding.UTF8)));
    }
}

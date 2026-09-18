import type {
  Finding,
} from "@/types/api";



function CategoryLabel(
  category: string,
) {

  return category
    .replaceAll("_", " ")
    .replace(
      /^./,
      char => char.toUpperCase(),
    );

}




function CategoryColor(
  category: string,
) {

  switch(category) {

    case "market":
      return "var(--primary)";


    case "customer":
      return "var(--primary)";


    case "competition":
      return "var(--primary)";


    case "technology":
      return "var(--primary)";


    case "business":
      return "var(--primary)";


    case "skeptic":
      return "var(--primary)";


    default:
      return "var(--muted)";

  }

}




export default function FindingCard(
  {
    finding,
  }: {
    finding: Finding;
  },
) {


  const categoryColor =
    CategoryColor(
      finding.category,
    );



  return (

    <article
      className="
        rounded-2xl
        border
        border-[var(--border)]
        bg-[var(--card)]
        p-6
        transition
        hover:bg-[var(--background)]
      "
    >


      <div
        className="
          flex
          items-start
          justify-between
          gap-4
        "
      >


        <span
          className="
            rounded-full
            border
            px-3
            py-1
            text-xs
            font-medium
            uppercase
          "
          style={{
            color: categoryColor,
            borderColor: categoryColor,
          }}
        >
          {
            CategoryLabel(
              finding.category,
            )
          }
        </span>



        <span
          className="
            rounded-full
            px-3
            py-1
            text-sm
            font-semibold
          "
          style={{
            color:
              "var(--success)",

            backgroundColor:
              "color-mix(in srgb, var(--success) 10%, transparent)",
          }}
        >
          {finding.confidence}%
        </span>


      </div>





      <h3
        className="
          mt-5
          text-xl
          font-bold
          text-[var(--foreground)]
        "
      >
        {finding.title}
      </h3>





      <p
        className="
          mt-3
          leading-7
        "
        style={{
          color:
            "var(--muted)",
        }}
      >
        {finding.summary}
      </p>



    </article>

  );

}
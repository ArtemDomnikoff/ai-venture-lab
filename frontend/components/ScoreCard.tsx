interface Props {
  score: number;
}



function ScoreColor(
  score: number,
) {

  if (score >= 80) {
    return "var(--success)";
  }


  if (score >= 50) {
    return "var(--warning)";
  }


  return "var(--danger)";

}



export default function ScoreCard(
  {
    score,
  }: Props,
) {


  const percentage =
    Math.min(
      Math.max(score, 0),
      100,
    );


  const rotation =
    `${percentage * 3.6}deg`;


  const color =
    ScoreColor(
      percentage,
    );



  return (

    <div
      className="
        flex
        flex-col
        items-center
        justify-center
        gap-4
      "
    >


      <div
        className="
          relative
          flex
          h-36
          w-36
          items-center
          justify-center
          rounded-full
          transition-all
          duration-700
          sm:h-44
          sm:w-44
        "
        style={{
          background:
            `conic-gradient(
              ${color}
              ${rotation},
              var(--border)
              ${rotation}
            )`,
        }}
      >


        <div
          className="
            flex
            h-28
            w-28
            items-center
            justify-center
            rounded-full
            bg-[var(--card)]
            sm:h-32
            sm:w-32
          "
        >


          <div
            className="
              text-center
            "
          >

            <div
              className="
                text-4xl
                font-bold
                text-[var(--foreground)]
                sm:text-5xl
              "
            >
              {percentage}
            </div>


            <div
              className="
                text-sm
                text-[var(--muted)]
              "
            >
              /100
            </div>


          </div>


        </div>


      </div>



      <div
        className="
          text-sm
          text-[var(--muted)]
        "
      >
        Venture score
      </div>


    </div>

  );

}
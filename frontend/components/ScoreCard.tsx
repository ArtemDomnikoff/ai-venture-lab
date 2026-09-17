interface Props {
  score: number;
}



function ScoreColor(
  score:number,
) {

  if(score >= 80) {
    return "var(--success)";
  }


  if(score >= 50) {
    return "var(--warning)";
  }


  return "var(--danger)";

}



function ScoreLabel(
  score:number,
) {

  if(score >= 80) {
    return "Strong";
  }


  if(score >= 50) {
    return "Moderate";
  }


  return "Weak";

}





export default function ScoreCard(
  {
    score,
  }:Props,
) {


  const percentage =
    Number.isFinite(score)
      ? Math.min(
          Math.max(
            score,
            0,
          ),
          100,
        )
      : 0;



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
        gap-5
      "
    >



      <div
        className="
          relative
          h-44
          w-44
          rounded-full
        "
        style={{
          background:
            `conic-gradient(
              ${color}
              ${percentage * 3.6}deg,
              var(--border)
              ${percentage * 3.6}deg
            )`,
        }}
      >



        <div
          className="
            absolute
            inset-3
            flex
            items-center
            justify-center
            rounded-full
            bg-[var(--card)]
          "
        >


          <div
            className="
              text-center
            "
          >


            <div
              className="
                text-5xl
                font-bold
                text-[var(--foreground)]
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
          text-center
        "
      >

        <div
          className="
            text-sm
            font-semibold
          "
          style={{
            color,
          }}
        >
          {ScoreLabel(
            percentage,
          )}
        </div>



        <div
          className="
            mt-1
            text-sm
            text-[var(--muted)]
          "
        >
          Venture score
        </div>


      </div>


    </div>

  );

}
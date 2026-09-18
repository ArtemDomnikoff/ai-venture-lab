export default function DashboardPage() {

  return (
    <section>

      <h1 className="text-3xl font-bold">
        Dashboard
      </h1>


      <p className="mt-3 text-zinc-400">
        Monitor your venture research agents.
      </p>


      <div
        className="
        mt-8
        grid
        grid-cols-3
        gap-6
        "
      >

        <Card
          title="Projects"
          value="0"
        />


        <Card
          title="Running Agents"
          value="0"
        />


        <Card
          title="Completed Runs"
          value="0"
        />

      </div>


    </section>
  );
}


function Card(
  {
    title,
    value,
  }:
  {
    title:string;
    value:string;
  }
){

  return (

    <div
      className="
      rounded-xl
      border
      border-zinc-800
      bg-zinc-900
      p-6
      "
    >

      <div className="text-sm text-zinc-400">
        {title}
      </div>

      <div className="mt-2 text-3xl font-bold">
        {value}
      </div>


    </div>

  );
}
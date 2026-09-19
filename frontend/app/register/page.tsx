import AuthForm from "@/components/AuthForm";


interface RegisterPageProps {
  searchParams: Promise<{
    next?: string;
  }>;
}


export default async function RegisterPage({
  searchParams,
}: RegisterPageProps) {
  const params = await searchParams;

  return (
    <main
      className="
        flex
        min-h-screen
        items-center
        justify-center
        px-6
      "
    >
      <AuthForm
        mode="register"
        nextPath={params.next}
      />
    </main>
  );
}

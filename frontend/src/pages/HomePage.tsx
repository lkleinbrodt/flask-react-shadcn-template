import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const HomePage = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Welcome to PLACEHOLDER_PROJECT_NAME!</CardTitle>
        <CardDescription>
          This is the homepage. Edit `src/pages/HomePage.tsx` to get started.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p>Your Flask and React application is up and running.</p>
      </CardContent>
    </Card>
  );
};

export default HomePage;

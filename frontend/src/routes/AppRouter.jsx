import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import appRoutes from './index'

const AppRouter = () => {
	return (
		<Router>
			<Routes>
				{appRoutes.map((route, index) => (
					<Route key={index} {...route} />
				))}
			</Routes>
		</Router>
	)
}

export default AppRouter
